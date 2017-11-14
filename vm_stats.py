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
    print "VM stats for " +  theJSON["sysinfo"]["hostname"] + "\tpps=Packets Per Second\teps=Errors per Second"
    for stat in theJSON["stats"]:
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['VM Port','switch','vnic_dev','txpps','txpps_drv','txeps','txeps_drv','txmbps','txmbps_drv','rxpps','rxpps_drv','rxeps','rxeps_drv','rxmbps','rxmbps_drv'])
	for port in stat["ports"]:
	    if "vnic" in port:
	       devname=port["vmnic"]["devname"]
	       txpps_drv=port["vmnic"]["txpps"]
	       txeps_drv=port["vmnic"]["txeps"]
	       txmbps_drv=port["vmnic"]["txmbps"]
	       rxpps_drv=port["vmnic"]["rxpps"]
	       rxeps_drv=port["vmnic"]["rxeps"]
	       rxmbps_drv=port["vmnic"]["rxmbps"]
	       table.add_row([port["name"],port["switch"],devname,port["txpps"],txpps_drv,port["txeps"],txeps_drv,port["txmbps"],txmbps_drv,port["rxpps"],rxpps_drv,port["rxeps"],rxeps_drv,port["rxmbps"],rxmbps_drv])
    print table
if __name__ == "__main__":
  main()
 
