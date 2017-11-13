import json
from prettytable import PrettyTable
fn=sys.argv[0]
print "File "+fn
def main():
 f=open("netstats-logs")
 theJSON=json.load(f)
 if "hostname" in theJSON["sysinfo"]:
    print "Stats for " +  theJSON["sysinfo"]["hostname"]
    for stat in theJSON["stats"]:
        print "Iteration Number="+ str(stat["iteration"])
	table = PrettyTable(['Port','txpps','txmbps','txsize','rxpps','rxmbps','rxsize'])
	for port in stat["ports"]:
	    table.add_row([port["name"],port["txpps"],port["txmbps"],port["txsize"],port["rxpps"],port["rxmbps"],port["rxsize"]])
	print table

    
if __name__ == "__main__":
  main()
 
