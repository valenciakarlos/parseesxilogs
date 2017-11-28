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
    print "Threads inventory for " +  theJSON["sysinfo"]["hostname"]
    for stat in theJSON["stats"]: # Traversing a list
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['Port','Switch','Thread Id','Name','Usage','Ready','Cstp'])
	# Capture the sys dictionary
	sys_dict=stat["sys"]
	for port in stat["ports"]:
	  if "sys" in port:
	    for thread in port["sys"]:
	        table.add_row([port["name"],port['switch'],thread,sys_dict[thread]["name"],sys_dict[thread]["used"],sys_dict[thread]["ready"],sys_dict[thread]["cstp"]])
        print table
    
if __name__ == "__main__":
  main()
 
