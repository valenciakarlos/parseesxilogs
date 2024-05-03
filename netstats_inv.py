# net stats inventory
# Traverse netstats file and extract all possible fields that could be relevant
# Leverages helper functions to create multiple pretty tables that we could later use
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



    vnic_auto_table = PrettyTable ()
    vmnic_auto_table = PrettyTable ()
    vnic_details_table = PrettyTable()

    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            if "vnic" in port:
                vnic_auto_table=helper_functions.build_pretty_table(port, vnic_auto_table)
                vnic_details_table = helper_functions.build_pretty_table ( port["vnic"], vnic_details_table )
            if "vmnic" in port:
                vmnic_auto_table=helper_functions.build_pretty_table(port, vmnic_auto_table)



    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            if "vnic" in port:
                helper_functions.populate_pretty_table(port, vnic_auto_table)
                helper_functions.populate_pretty_table ( port["vnic"], vnic_details_table )
            if "vmnic" in port:
                helper_functions.populate_pretty_table ( port, vmnic_auto_table )



    print("---- Vnic Auto Table ----")
    print("Columns added automatically:")
    print(vnic_auto_table.field_names)
    vnic_auto_table.set_style ( MSWORD_FRIENDLY )
    print(vnic_auto_table.get_string(fields=["name", "id","lcore", "txpps", "rxpps", "txeps", "rxeps"]))

    print("---- Vnic->vnic Auto Table ----")
    print(vnic_details_table.field_names)
    vnic_details_table.set_style ( MSWORD_FRIENDLY )
    print(vnic_details_table.get_string(fields=['ring1sz', 'ring2sz','r1full', 'r2full', 'sgerr', 'tsopct', 'tsotputpct', 'txucastpct', 'txeps', 'lropct', 'lrotputpct', 'rxucastpct', 'rxeps', 'maxqueuelen', 'requeuecnt','dropsByBurstQ', 'droppedbyQueuing']))


    print("---- VMNIC Auto Table ----")
    print("Columns added automatically:")
    print(vmnic_auto_table.field_names)
    vmnic_auto_table.set_style ( MSWORD_FRIENDLY )
    print ( vmnic_auto_table.get_string ( fields=["name", "id", "lcore", "txpps", "txeps", "txmbps", "rxpps", "rxeps", "rxmbps"] ) )





    '''
    
    If we want to dump the table to a csv

    print ( f"Results saved to nic_inv_{filename_without_extension}.csv" )




    with open('nic_inv_' + filename_without_extension + '.csv','w', newline='') as f_output:
        f_output.write(table.get_csv_string())
        
    '''



if __name__ == "__main__":
    main()
