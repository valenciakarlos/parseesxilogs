import json
import sys
from prettytable import PrettyTable
if (len(sys.argv)==1):
   print "Please enter schedstats file to parse"
   exit

def main():
 if (len(sys.argv)==1):
    print "Trying to locate local file schedstats-logs"
    f=open("schedstats.logs")
    netstats_file=("netstats.logs")
 else:
    sched_stats_file=sys.argv[1]
    schd_f=open(sched_stats_file)
    # Also try to open the accompanying netstats file
    srv_name=sched_stats_file.split('_',1)[0]
    netstats_file=srv_name+"_netstats.logs"
    print "Opening files "+sched_stats_file+" and "+netstats_file
    net_f=open(netstats_file)

    
 theJSON=json.load(net_f)
 # Using pandas to parse the sched stats file
 import pandas as pd
 df=pd.read_table(sched_stats_file,sep='\s+')
 # Exstracting the non-zero CPUs
 for idx,thread in enumerate(df.exclusiveTo):
     if not (thread==0):
        print "Index="+str(idx)+" Thread="+str(thread)+" CPU="+str(df.cpu[idx])+" Node="+str(df.node[idx])

 if "hostname" in theJSON["sysinfo"]:
    print "CPU stats for " +  theJSON["sysinfo"]["hostname"]
    for stat in theJSON["stats"]: # Traversing a list
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['Name','Id','used','latencySensitivity','exclaff'])
	vcpus_dict=stat["vcpus"]
	for vcpuId,vcpu_attrib in vcpus_dict.iteritems():  # Traversing a dictionary
	    if "latencySensitivity" in vcpu_attrib:  # Some of the CPU stats dont have latency sensitivity and exclaff so need to validate for that
	       latSen=vcpu_attrib["latencySensitivity"]
	       exclaff=vcpu_attrib["exclaff"]
	    else:
	       latSen="NA"
	       exclaff="NA"
	    table.add_row([vcpu_attrib["name"],vcpu_attrib["id"],vcpu_attrib["used"],latSen,exclaff])
	print table

    
if __name__ == "__main__":
  main()
 
