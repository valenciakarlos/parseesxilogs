import json
import sys
#Reference https://pypi.org/project/prettytable/
from prettytable import PrettyTable
# To change the Style
# Options are:
#
#    DEFAULT - The default look, used to undo any style changes you may have made
#    PLAIN_COLUMNS - A borderless style that works well with command line programs for columnar data
#    MARKDOWN - A style that follows Markdown syntax
#    ORGMODE - A table style that fits Org mode syntax
#    SINGLE_BORDER and DOUBLE_BORDER - Styles that use continuous single/double border lines with Box drawing characters for a fancier display on terminal

from prettytable import PLAIN_COLUMNS




if (len(sys.argv) == 1):
    print("Please enter file netstats file to parse")
    exit()


def main():
    print("Arguments=" + str(len(sys.argv)))
    if (len(sys.argv) == 1):
        print("Trying to locate local file netstats-logs")
        f = open("netstats-logs")
    else:
        print("Opening file " + sys.argv[1])
        f = open(sys.argv[1])
    theJSON = json.load(f)
    if "hostname" in theJSON["sysinfo"]:
        print("Stats for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:
            print("Iteration Number=" + str(stat["iteration"]))
            table = PrettyTable(['Port', 'switch', 'txpps', 'txmbps','txsize', 'rxpps', 'rxmbps','rxsize','rxmode','tunemode','ens','uplink','mac'])
            # We might want to display the lcores here as well

            for port in stat["ports"]:

                table.add_row(
                    [port["name"], port["switch"], port["txpps"], port["txmbps"],port['txsize'], port["rxpps"], port["rxmbps"],port["rxsize"],port["rxmode"],port["tunemode"],port["ens"],port["uplink"],port["mac"]])
            # Still trying to figure out this float format so I can put comma separators (ref https://www.geeksforgeeks.org/formatting-integer-column-of-dataframe-in-pandas/)
            # And : https://pypi.org/project/prettytable/

            table.float_format = '.1'

            #table.set_style(PLAIN_COLUMNS)

            from prettytable import MSWORD_FRIENDLY
            table.set_style(MSWORD_FRIENDLY)
            print(table.get_string(fields=["Port","switch","rxmode","tunemode","ens","uplink","mac"]))


if __name__ == "__main__":
    main()
