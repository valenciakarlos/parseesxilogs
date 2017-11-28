import json
import sys
from prettytable import PrettyTable
if (len(sys.argv)==1):
   print "Please enter file netstats file to parse"
   exit

def main():
 if (len(sys.argv)==1):
    print "Trying to locate local file netstats-logs"
    f=open("netstats-logs")
 else:
    print "Opening file "+sys.argv[1]
    f=open(sys.argv[1])
 theJSON=json.load(f)
 if "hostname" in theJSON["sysinfo"]:
    print "Sys stats for " +  theJSON["sysinfo"]["hostname"]
    for stat in theJSON["stats"]: # Traversing a list
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['Name','Id','used','latencySensitivity','exclaff','sysoverlap'])
	sys_dict=stat["sys"]
	for sysId,sys_attrib in sys_dict.iteritems():  # Traversing a dictionary
	    table.add_row([sys_attrib["name"],sys_attrib["id"],sys_attrib["used"],sys_attrib["latencySensitivity"],sys_attrib["exclaff"],sys_attrib["sysoverlap"]])
	print table

    
if __name__ == "__main__":
  main()
 
