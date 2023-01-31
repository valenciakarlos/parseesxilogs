import json
import sys
from prettytable import PrettyTable
if (len(sys.argv)==1):
   print("Please enter file netstats file to parse")
   exit()

def main():
 if (len(sys.argv)==1):
    print("Trying to locate local file netstats-logs")
    f=open("netstats-logs")
 else:
    print("Opening file " + sys.argv[1])
    f=open(sys.argv[1])
 theJSON=json.load(f)
 if "hostname" in theJSON["sysinfo"]:
    print("Stats for " + theJSON["sysinfo"]["hostname"] + "pps=Packets Per Second")
    for stat in theJSON["stats"]:
        print("Iteration Number=" + str(stat["iteration"]))
        table = PrettyTable(['Port','switch','txpps','txeps','txmbps','txsize','txq_cnt','rxpps','rxeps','rxmbps','rxsize','rxq_cnt'])
    for port in stat["ports"]:
        if "txqueue" in port:
           txq_cnt=port["txqueue"]["count"]
        else:
           txq_cnt="NA"
        if "rxqueue" in port:
           rxq_cnt=port["rxqueue"]["count"]
        else:
           rxq_cnt="NA"
        table.add_row([port["name"],port["switch"],port["txpps"],port["txeps"],port["txmbps"],port["txsize"],txq_cnt,port["rxpps"],port["rxeps"],port["rxmbps"],port["rxsize"],rxq_cnt])
    print(table)


if __name__ == "__main__":
  main()
 
