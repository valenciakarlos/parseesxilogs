# vmkstatsview.py: a more convenient vmkstats viewer
#
# This tool is used to view vmkstats (ESXi CPU profile) in text format.
# Compared to existing tools:
# 1. It uses Python so it can run directly on ESXi (and anywhere with Python3).
#    Prevuously we need to copy data to Linux to use a Java/Perl based viewer.
# 2. It can output offset data to find hot paths/instructions within functions.
#    Current viewer always aggregates samples at functions so offsets are lost.
#    This can be enabled for all functions or top-of-callstack functions only.
#    Offsets at leaf level (e.g. recorded RIP) may be off by some instructions
#    due to skid, but can still be useful to locate hot regions in fucntions.
# 3. Provides filter based on called function or top-of-callstack function.
# 4. Provides min sample count or ratio filter, to hide very cold paths.
# 5. When running on ESXi it can also do vmkstats collection first, if needed,
#    saving a few manual vmkstatsdumper / vsish commands.

import sys
import argparse

curLine = 0
minCnt = 0
minCntSelf = 0
minFiltered = 0

def printProfile(tree, indent, totalCnt, parentLine):
  global curLine
  width = len(tree)
  idx = 0
  for k, v in sorted(tree.items(), key=lambda x: x[1][1], reverse=True):
    idx += 1
    if v[1] >= minCnt and (v[2] >= minCntSelf or (v[1] >= minCntSelf and len(v[0]))):
      curLine += 1
      print("L%04x %sP%04x->[%.2f, %.2f]%s %d, %d" % (\
            curLine, indent + (" " if width == 1 else "|"), parentLine,
            (v[1] / totalCnt) * 100.0, (v[2] / totalCnt) * 100.0, k, v[1], v[2]))
    else:
      global minFiltered
      minFiltered += v[2]
    if len(v[0]):
      printProfile(v[0], indent + ("  " if idx == width else "| ") , totalCnt, curLine)

def main():
  parser = argparse.ArgumentParser(usage="vmkstatsview.py worldID [options]")
  parser.add_argument("worldID", type=int,
                      help="WID of world to view vmkstats (CPU profile)")
  parser.add_argument("-e", "--callee", action="store_true",
                      help="Display callee root trees instead of caller root trees")
  parser.add_argument("-p", "--path", default=".",
                      help="Path to vmkstats raw data. Default to current path")
  parser.add_argument("-o", "--offset", action="store_true",
                      help="Show function offsets. By default offsets are ignored in aggregation"
                           " and display. Conflicts with -L.")
  parser.add_argument("-L", "--leaf_offset", action="store_true",
                      help="Display function offset for leaf (top of stack) addresses only."
                           " Conflicts with -o and -e.")
  parser.add_argument("-f", "--function",
                      help="Only use callstacks containing the specified function")
  parser.add_argument("-t", "--topofstack",
                      help="Only use callstacks with the specified function at top-of-stack")
  parser.add_argument("-m", "--min", default=0, type=float,
                      help="Skip printing items with count or ratio lower than this number."
                           " A number >=1 specifies count, between 0 to 1 specifies ratio")
  parser.add_argument("-M", "--minself", default=0, type=float,
                      help="Skip printing items with self count or self ratio lower than"
                           " this number, e.g., not including its childrens' counts.")
  parser.add_argument("-c", "--collect", action="store_true",
                      help="Collects vmkstats before displaying the result (run on ESXi only)")
  parser.add_argument("-d", "--duration", default=0, type=int,
                      help="For -c, collect vmkstats for the given duration (in seconds) instead"
                           " of wating for Ctrl+C.")
  args = parser.parse_args(sys.argv[1:])
  if args.leaf_offset and (args.offset or args.callee):
    print("--leaf_offset can't be used with --offset or --callee")
    return -1
  if args.min < 0 or args.minself < 0:
    print("--min and --minself should be greater than 0")
    return -1

  # Collect vmkstats, if asked.
  if args.collect:
    try:
      from vmware import vsi
    except:
      print("--colect works only on ESXi")
      return -1
    from time import sleep
    import os
    if args.path != "." and not os.path.exists(args.path):
      os.mkdir(args.path)
    vsi.set("/perf/vmkstats/command/stop", 1)
    vsi.set("/perf/vmkstats/command/reset", 1)
    vsi.set("/perf/vmkstats/command/start", 1)
    # Save ps -c output so one can find interested worldIDs
    os.system("ps -c > %s/ps_c.out" % args.path)
    if args.duration > 0:
      print("Collecting vmkstats for %d seconds" % args.duration)
      sleep(args.duration)
    else:
      print("Collecting vmkstats. Ctrl + C to stop.")
      try:
        while True:
          sleep(1)
      except KeyboardInterrupt:
        pass
    print("Done collecting. Dumping vmkstats data")
    vsi.set("/perf/vmkstats/command/stop", 1)
    vsi.set("/perf/vmkstats/command/drain", 1)
    os.system("vmkstatsdumper -a -o " + args.path)

  # Find valid samples (e.g. matches given worldID)
  print("Reading " + args.path + "/samples...")
  nSamples = 0
  csCnts = {}
  with open(args.path + "/samples") as f:
    f.readline()
    for line in f:
      s = line.split()
      wid = int(s[6])
      if wid != args.worldID:
        continue
      rip = int(s[0][2:], 16)
      csid = int(s[1])
      cnt = int(s[3])
      nSamples += cnt
      if not csid in csCnts:
        csCnts[csid] = {rip: cnt}
      else:
        csCnts[csid][rip] = csCnts[csid].get(rip, 0) + cnt
  if not nSamples:
    print("No sample for world %d" % args.worldID)
    return 0
  print("%d samples for world %d" % (nSamples, args.worldID))
  global minCnt, minCntSelf
  minCnt = args.min if args.min > 1 else args.min * nSamples
  minCntSelf = args.minself if args.minself > 1 else args.minself * nSamples

  # Find callstacks referenced in valid samples, and unique addresses in the stacks
  addrs = set()
  stacks = []
  with open(args.path + "/callStacks") as f:
    f.readline()
    for line in f:
      s = line.split()
      if len(s) < 2:
        continue
      csid = int(s[0])
      cnts = csCnts.get(csid, None)
      if not cnts:
        continue
      for rip, cnt in cnts.items():
        stack = [rip] + [int(x[2:], 16) for x in s[1:]]
        addrs = addrs.union(stack)
        stacks.append((stack, cnt))
  print("Done parsing callstacks")

  # Create a table for translating an address (VA) to symbol+offset
  addrs = sorted(list(addrs))
  va2sym = {}
  gateEntryBegin = 0
  gateEntryEnd = 0
  with open(args.path + "/symbolTable.k") as f:
    lowest = addrs[0]
    for line in f:
      s = line.split()
      va = int(s[0], 16)
      size = int(s[1], 16)
      if lowest < va:
        continue
      # Find the address of gate_entry to re-root stacks that has it
      if not gateEntryBegin and s[2] == "gate_entry":
        gateEntryBegin = va
        gateEntryEnd = va + size
      while lowest <= va + size:
        va2sym[lowest] = (s[2], lowest - va)
        addrs.remove(lowest)
        if not len(addrs):
          break
        lowest = addrs[0]
      if not len(addrs):
        break

  root = {}
  for s in stacks:
    stack = s[0]
    cnt = s[1]
    # Filter based on top of stack function
    if args.topofstack and va2sym[stack[0]][0] != args.topofstack:
        continue
    # Truncate callstack to gate_entry (e.g. interrupt), if it exists
    end = len(stack)
    for i, addr in enumerate(stack):
      if addr >= gateEntryBegin and addr <= gateEntryEnd:
        end = i
        break
    stack = stack[:end]
    # Filter based on function. Need to do this after gate_entry truncation.
    if args.function:
      skip = True
      for addr in stack:
        if va2sym[addr][0] == args.function:
          skip = False
          break
      if skip:
        continue
    # Merge callstack to tree
    depth = len(stack)
    tree = root
    tos = (depth - 1) if args.callee else 0
    for addr in (stack if args.callee else reversed(stack)):
      depth -= 1
      (fn, ofs) = va2sym[addr]
      name = "%s+%d(%x)" % (fn, ofs, addr) if args.offset or (args.leaf_offset and not depth)\
             else fn
      branch = tree.get(name, ({}, 0, 0))
      tree[name] = (branch[0], branch[1] + cnt, branch[2] + (cnt if depth == tos else 0))
      tree = branch[0]

  if args.offset or args.leaf_offset:
    print("Note: actual instruction is the one before the indicated offset. Leaf-level offset "
          "may be off by a few instructions due to skid.")
  if args.function:
    print("Displaying only samples that has function %s on the stack" % args.function)
  if args.topofstack:
    print("Displaying only samples that has function %s at the top-of-stack" % args.topofstack)
  print("Line# ParentLine#->[%Time, %TimeSelf]FnName+Offset(Address) SampleCnt, SampleCntSelf")
  printProfile(root, "", nSamples, 0)
  if minFiltered > 0:
    print("Filtered out %d (%.2f%% of total) samples with --min/--minself" %\
          (minFiltered, (minFiltered / nSamples) * 100.0))

if __name__ == "__main__":
  sys.exit(main())
