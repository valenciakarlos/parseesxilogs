import json
import sys

#Reference https://pypi.org/project/prettytable/
from prettytable import PrettyTable
from prettytable import MSWORD_FRIENDLY

# To change the Style
# Options are:
#
#    DEFAULT - The default look, used to undo any style changes you may have made
#    PLAIN_COLUMNS - A borderless style that works well with command line programs for columnar data
#    MARKDOWN - A style that follows Markdown syntax
#    ORGMODE - A table style that fits Org mode syntax
#    SINGLE_BORDER and DOUBLE_BORDER - Styles that use continuous single/double border lines with Box drawing characters for a fancier display on terminal

from prettytable import PLAIN_COLUMNS

import helper_functions


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
        import os
        filename_without_extension, file_extension = os.path.splitext ( sys.argv[1] )


    theJSON = json.load(f)

    #Commenting out autotable for now 
    '''

    vnic_auto_table = PrettyTable ()
    #vmnic_auto_table = PrettyTable ()
    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            if "vnic" in port:
                vnic_auto_table=helper_functions.build_pretty_table(port, vnic_auto_table)

    print("Generated automatic table for vnics is:")
    print(vnic_auto_table)


    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            if "vnic" in port:
                helper_functions.populate_pretty_table(port, vnic_auto_table)

    vnic_auto_table.set_style ( MSWORD_FRIENDLY )
    print(vnic_auto_table.get_string(fields=["name", "id","lcore", "txpps", "rxpps", "txeps", "rxeps"]))
    '''










    if "hostname" in theJSON["sysinfo"]:
        print("Stats for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:
            print("Iteration Number=" + str(stat["iteration"]))
            table = PrettyTable(['Port', 'switch', 'txpps', 'txmbps','txsize','txeps', 'rxpps', 'rxmbps','rxsize','rxeps','ens','uplink','mac','id','lcorein', 'lcoreout'])
            # We might want to display the lcores here as well

            for port in stat["ports"]:
                if "lcore" in port:
                    lcoresin=(port["lcore"][0]['in'])
                    lcoresout = (port["lcore"][0]['out'])
                    lcoresinstr=' '.join(lcoresin)
                    lcoresoutstr = ' '.join(lcoresout)
                else:
                    lcoresinstr="NA"
                    lcoresoutstr="NA"
                table.add_row(
                    [port["name"], port["switch"], port["txpps"], port["txmbps"],port["txsize"], port["txeps"], port["rxpps"], port["rxmbps"],port["rxsize"],port["rxeps"],port["ens"],port["uplink"],port["mac"],port["id"],lcoresinstr, lcoresoutstr])
            # Still trying to figure out this float format so I can put comma separators (ref https://www.geeksforgeeks.org/formatting-integer-column-of-dataframe-in-pandas/)
            # And : https://pypi.org/project/prettytable/

            table.float_format = '.1'

            #table.set_style(PLAIN_COLUMNS)


            table.set_style(MSWORD_FRIENDLY)
            print(table)
            #print(table.get_string(fields=["Port","switch","id","tunemode","ens","uplink","mac","lcorein","lcoreout"]))
            # Dumping pretty table to a csv



            print ( f"Results saved to nic_inv_{filename_without_extension}.csv" )




            with open('nic_inv_' + filename_without_extension + '.csv','w', newline='') as f_output:
                f_output.write(table.get_csv_string())



if __name__ == "__main__":
    main()
