import json
import sys
from prettytable import PrettyTable

# This one inventories the CPUs mapped to NUMA and then it list all threads that have exclussive afinity.
# One could use that to verify that ALL threads on one VMs are mapped to the same NUMA

if len(sys.argv) == 1:
    print("Please enter file netstats file to parse")
    exit()


def main():
    if len(sys.argv) == 1:
        print("Trying to locate local file netstats-logs")
        f = open("netstats-logs")
    else:
        print("Opening file " + sys.argv[1])
        f = open(sys.argv[1])
    theJSON = json.load(f)
    if "hostname" in theJSON["sysinfo"]:
        print("Sys stats for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:  # Traversing a list
            print("Iteration Number=" + str(stat["iteration"]))
            table = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'exclaff', 'sysoverlap','lcoreusage','pps'])
            table_exclaff = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'exclaff', 'sysoverlap','lcoreusage','pps'])
            sys_dict = stat["sys"]

            for sysId, sys_attrib in sys_dict.items():  # Traversing the sys dictionary sysId is the Key sys_attrib is the associated attributes
                if "lcoreusage" in sys_attrib:
                    lcoreusage=sys_attrib["lcoreusage"]
                else:
                    lcoreusage="-"
                if "pps" in sys_attrib:
                    pps=sys_attrib["pps"]
                else:
                    pps="-"

                if "latencySensitivity" in sys_attrib:
                    latsen=sys_attrib["latencySensitivity"]
                else:
                    latsen="-"


                if "exclaff" in sys_attrib:
                    exclaff=sys_attrib["exclaff"]
                    if not exclaff == -1:
                      table_exclaff.add_row(
                        [sys_attrib["name"], sys_attrib["id"], sys_attrib["used"], latsen,
                         sys_attrib["exclaff"], sys_attrib["sysoverlap"],lcoreusage,pps])
                else:
                    exclaff="-"

                table.add_row(
                    [sys_attrib["name"], sys_attrib["id"], sys_attrib["used"], latsen,
                     exclaff, sys_attrib["sysoverlap"],lcoreusage,pps])

 

            from prettytable import MSWORD_FRIENDLY
            table.set_style(MSWORD_FRIENDLY)
            print(table)
            print("Entires with exclussive affinity")

            table_exclaff.set_style(MSWORD_FRIENDLY)
            print(table_exclaff)


if __name__ == "__main__":
    main()
