# Parse the text files into JSON for easier processing
# Reference: https://www.geeksforgeeks.org/convert-text-file-to-json-in-python/

import json
import sys
from prettytable import PrettyTable

#if (len(sys.argv) == 1):
#    print("Please enter file to parse")
#    exit()

# We want to have a similar structure to the one seen on netstasts
# stats: Array ob objects with time, interval, iteration, and object
# Conversion rule:
#Python object	    JSON object
#dict	            object
#list, tuple	    array
#str	            string
#int, long, float	numbers
#True	            true
#False	            false
#None	            null


def main():



        # Basic parse into json of space separated values
        # Want this structure:
        # { "sysinfo": Dictionary with { "filename": "file" },
            # "stats": [Array of stats dictionaries ]
        # }
        #
        # stats_dict { interval: ##, iteration ##, ports [Array of ports] }
        #
        # port: { Dictionary with all the other stats }

        # We want to match: space separated stats (process with split below)
        # Colon separated stats (process same as above)
        # The rest needs to be matched out
        # Stats on columns with headers (process with pandas)

        base_dir="/Users/vcarlos/Library/CloudStorage/OneDrive-VMware,Inc/VMware/Partner Work/Ericsson/L2_Steering/Slowpath issue/ens_diagnostics_2023-03-20T16:42:26+0000/"

        basic_space_sep_stats= base_dir + "basic_stats.txt"

        colon_separated_basic = base_dir + "basic-vsi-pnic-stats.txt"
        colon_separated_stats = base_dir + "vsi-pnic-stats.txt"

        dict1={}
        with open(basic_space_sep_stats) as fh:
            for line in fh:
                    # reads each line and trims of extra the spaces
                    # and gives only the valid words
                    key, value = line.strip().split(None, 1)
                    dict1[key] = value.strip()
            print("\nDictionary of space separated")
            print(dict1)


        new_dict={}
        with open(colon_separated_basic) as fh:
            for line in fh:
                    # reads each line and trims of extra the spaces
                    # and gives only the valid words
                    key, value = line.strip().split(':', 1)
                    new_dict[key] = value.strip()
            print("\nDictionary of colon separated")
            print(new_dict)

        basic_flow_stats_file= base_dir + "ens-flow-stats-table.txt"
        # Format: Need to parse those damn columns
        #### First sample for lcore 0:

        #lcoreID  numFlows   hits           miss           fpoHits        localHits      keyInsertFailCount   latSampleCount
        #-------------------------------------------------------------------------------------------------------------------
        #0        5          3134387330     2443324784     0              1928163285     0                    0

        # Reference: https://pandas.pydata.org/docs/reference/general_functions.html
        # https://www.datacamp.com/tutorial/pandas?utm_source=google&utm_medium=paid_search&utm_campaignid=19589720821&utm_adgroupid=143216588577&utm_device=c&utm_keyword=&utm_matchtype=&utm_network=g&utm_adpostion=&utm_creative=645433043010&utm_targetid=aud-392016246653:dsa-1947282172981&utm_loc_interest_ms=&utm_loc_physical_ms=9000685&utm_content=dsa~page~community-tuto&utm_campaign=230119_1-sea~dsa~tutorials_2-b2c_3-row-p1_4-prc_5-na_6-na_7-le_8-pdsh-go_9-na_10-na_11-na-marayc23&gclid=Cj0KCQjwlPWgBhDHARIsAH2xdNfaVh9Px2DODCuB-q3r64gVroRKnCLZiVkJL8uOu8WkXyXlyqqzwn8aAl7dEALw_wcB

        print("\nExporting lcore stats to a df using pandas. Easy to do if file is parsed properly")
        import pandas as pd

        df=pd.read_csv(basic_flow_stats_file, delim_whitespace=True)
        print(df)
        # Note: As long as it is well formatted dumping to pandas makes things easier. Maybe we can read line by line to a DF and then dump to a json structure

        # Now the hard part. Parse the non-standar stuff
        space_sep_stats = base_dir + "ens-port-stats.txt"
        # And separate into a json object








if __name__ == "__main__":
    main()
