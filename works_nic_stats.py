import json
import sys
from prettytable import PrettyTable
if (len(sys.argv)==1):
   print "Please enter file netstats file to parse"
   exit

def main():
 print "Arguments="+str(len(sys.argv))
 if (len(sys.argv)==1):
    print "Trying to locate local file netstats-logs"
    f=open("netstats-logs")
 else:
    print "Opening file "+sys.argv[1]
    f=open(sys.argv[1])
 theJSON=json.load(f)
 if "hostname" in theJSON["sysinfo"]:
    print "Stats for " +  theJSON["sysinfo"]["hostname"]
    for stat in theJSON["stats"]:
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['Port','switch','txpps','txmbps','txsize','rxpps','rxmbps','rxsize'])
	for port in stat["ports"]:
	    table.add_row([port["name"],port["switch"],port["txpps"],port["txmbps"],port["txsize"],port["rxpps"],port["rxmbps"],port["rxsize"]])
	print table

    
if __name__ == "__main__":
  main()
 
