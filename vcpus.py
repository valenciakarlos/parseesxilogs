import json
import sys
from prettytable import PrettyTable

if len(sys.argv) == 1:
    print("Please enter file netstats file to parse")
    exit()


def main():
    if (len(sys.argv) == 1):
        print("Trying to locate local file netstats-logs")
        f = open("netstats-logs")
    else:
        print("Opening file " + sys.argv[1])
        f = open(sys.argv[1])
    theJSON = json.load(f)
    if "hostname" in theJSON["sysinfo"]:
        print("CPU stats for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:  # Traversing a list
            print("Iteration Number=" + str(stat["iteration"]))
            table = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'exclaff'])
            table_exclaff = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'exclaff'])
            vcpus_dict = stat["vcpus"]
            for vcpuId, vcpu_attrib in vcpus_dict.  items():  # Traversing a dictionary
                if "latencySensitivity" in vcpu_attrib:  # Some of the CPU stats dont have latency sensitivity and exclaff so need to validate for that
                    latSen = vcpu_attrib["latencySensitivity"]
                    exclaff = vcpu_attrib["exclaff"]
                else:
                    latSen = "NA"
                    exclaff = "NA"
                table.add_row([vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff])
                if not exclaff == -1 or not exclaff == "NA":
                    table_exclaff.add_row(
                        [vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff])

        from prettytable import MSWORD_FRIENDLY
        table.set_style(MSWORD_FRIENDLY)
        print(table)
        print("entries with exclaff")

        table_exclaff.set_style(MSWORD_FRIENDLY)
        print(table_exclaff)


if __name__ == "__main__":
    main()
