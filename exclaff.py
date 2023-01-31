import json
import sys
from prettytable import PrettyTable

if (len(sys.argv) != 3):
    print("Usage : exclaff.py <sched_stats_file> <netstats_file>")
    exit()


def main():
    # Open schedule stats file (second argument)
    sched_stats_file = sys.argv[2]
    # Open netstats file (first argument)
    netstats_file = sys.argv[1]

    print("Opening files " + sched_stats_file + " and " + netstats_file)
    schd_f = open(sched_stats_file)
    net_f = open(netstats_file)

    theJSON = json.load(net_f)
    # Using pandas to parse the sched stats file
    import pandas as pd
    df = pd.read_table(sched_stats_file, sep='\s+')
    # Exstracting the non-zero CPUs
    thread_dict = {}
    # Threads
    table_sched = PrettyTable(['Cpu', 'Node', 'Thread'])
    print("Scheduler stats")
    for idx, thread in enumerate(df.exclusiveTo):
        if not (thread == 0):
            # Store info on dict with key being the thread id
            # print("Index=" + str(idx) + " Thread=" + str(thread) + " CPU=" + str(df.cpu[idx]) + " Node=" + str(df.node[idx]))
            table_sched.add_row([str(df.cpu[idx]), str(df.node[idx]), thread])
            thread_dict[thread] = {'cpu': str(df.cpu[idx]), 'node': str(df.node[idx])}

#    print(table_sched)

    # Traversing the cpu stats
    if "hostname" in theJSON["sysinfo"]:
        print("vCPU affinity info for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:
            print("Iteration Number=" + str(stat["iteration"]))
            #table = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'vcpu_exclaff'])
            table = PrettyTable(['Name','Id','used','latencySensitivity','vcpu_exclaff','node'])
            vcpus_dict = stat["vcpus"]

            for vcpuId, vcpu_attrib in vcpus_dict.items():  # Traversing a dictionary
                if "latencySensitivity" in vcpu_attrib:  # Some of the CPU stats dont have latency sensitivity and exclaff so need to validate for that
                    latSen = vcpu_attrib["latencySensitivity"]
                    exclaff = vcpu_attrib["exclaff"]
                else:
                    latSen = "NA"
                    exclaff = "NA"
                try:
                    mappedNode=(thread_dict[vcpu_attrib["id"]]["node"])
                except KeyError:
                    mappedNode="NA"
                table.add_row([vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff,mappedNode])
            print(table)


if __name__ == "__main__":
    main()
