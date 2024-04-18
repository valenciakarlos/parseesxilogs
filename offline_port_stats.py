# Calculates per port stats
'''
Expected format:
#### First sample for Switch 0 port 0:

txPkts                 0
txBytes                0
txMcastPkts            0
txMcastBytes           0
txBcastPkts            20
'''

import re
import pandas as pd
import argparse
from prettytable import PrettyTable
import time
import math


def validate_arguments():
    parser = argparse.ArgumentParser(description="Calculates per port stats")
    # The first argument, filename, is a positional argument (required).
    parser.add_argument("filename", help="Filename to parse")
    parser.add_argument( "-n", "--nicfile", type=str, help="CSV file with the NICs and port Id", default='nic_inv.csv' )
    # File must have portID labeled as id
    # Might want to pass a file with the mapping of port name and switch name. see nic_inv.py for details
    # For now will only do two iterations
    args = parser.parse_args()
    return args

# Calculate vectorized which is supposed to be cleaner. Results are added to the DF. Called from within the dataframe with apply
def calculate_ratios_vectorized(row):
    total_events = row['hits'] + row['miss'] + row['slowpath'] + row['localHits']
    total_hits = row['hits']+row['localHits']
    total_hits_and_miss = total_hits + row['miss']
    if (not total_events==0):
        slowpath_ratio = row['slowpath'] / total_events
        hits_ratio = total_hits / total_events
        miss_ratio = row['miss'] / total_events
    else:
        slowpath_ratio = 0
        hits_ratio = 0
        miss_ratio = 0

    if (not total_hits_and_miss==0):
        hits_to_miss_ratio=total_hits/total_hits_and_miss
        miss_to_hits_ratio=row['miss']/total_hits_and_miss
    else:
        hits_to_miss_ratio = 0
        miss_to_hits_ratio = 0




    return pd.Series({
        'slowpath_ratio': slowpath_ratio,
        'hits_ratio': hits_ratio,
        'miss_ratio': miss_ratio,
        'hits_to_miss_ratio': hits_to_miss_ratio,
        'miss_to_hits_ratio': miss_to_hits_ratio
    })



# Does some calculations if the DF has all the info we need
# Receives two data frames and provides the ratio of slow path to misses
def get_ratios(df_one,df_two):
    # Returns a dictionary with all the ratios calculated
    dict_ratios={}
    try:
        # Try to extract the value for the indexes we need
        hits=df_two.loc['hits',0]-df_one.loc['hits',0]
        miss=df_two.loc['miss',0]-df_one.loc['miss',0]
        slowpath=df_two.loc['slowpath',0]-df_one.loc['slowpath',0]
        localHits=df_two.loc['localHits',0]-df_one.loc['localHits',0]

        total_events=hits+miss+slowpath+localHits
        #dict_ratios['total_events']=total_events
        slowpath_ratio=slowpath/total_events
        dict_ratios['slowpath_ratio']=slowpath_ratio
        hits_ratio=(hits+localHits)/total_events
        dict_ratios['hits_ratio']=hits_ratio
        miss_ratio=miss/total_events
        dict_ratios['miss_ratio']=miss_ratio
        hits_to_miss_ratio=(hits+localHits)/(hits+localHits+miss)
        dict_ratios['hits_to_miss_ratio']=hits_to_miss_ratio
        miss_to_hits_ratio=miss/(hits+localHits+miss)
        dict_ratios['miss_to_hits_ratio']=miss_to_hits_ratio
        #print(f"Hits Ratio={hits_ratio:.2%} Slowpath ratio={slowpath_ratio:.2%} Miss ratio={miss_ratio:.2%} Hits to Miss ratio={hits_to_miss_ratio:.2%} Miss to Hits ratio={miss_to_hits_ratio:.2%} ")

    except KeyError:
        # Handle the case where the index does not exist
        print("Error could not extract some indexes")
    return dict_ratios


def get_nonzero_df(org_df):
    non_zero_cols=org_df.columns[org_df.any()]
    non_zero_df=org_df[non_zero_cols]
    return non_zero_df

def print_ratios(dict_ratios):
    # Gets a dictionary with ratios (all pct formatted) and prints it
    from prettytable import PrettyTable
    keys_list=list(dict_ratios.keys())
    table = PrettyTable(['Ratio','Value'])
    #table = PrettyTable(keys_list)
    for key, value in dict_ratios.items():
        table.add_row([key, '{:.2%}'.format(value)])
    print(table)



def find_number(string):
    # Extracts number for a like that looks like "string1: number string2"
    import re
    pattern = r'\b\d+\b'
    match=re.search(pattern,string)
    if match:
      return int(match.group())
    else:
       return 0


args = validate_arguments()
FILENAME = args.filename

# Open the file containing the text
agg_df = pd.DataFrame()
switch_port_data = {}

with open(FILENAME, "r") as file:
    # Read the contents of the file


    text = file.read()
    # Need to split this into multiple entries split at:
    # Split into two samples before / after the wait
    samples= re.split("######################## Waiting \d+ seconds ########################", text)
    #agg_df = pd.DataFrame()


    for index, sample in enumerate(samples):
        print("Sample "+ str(index))
        #json_entries = re.split("#### [First|Second] sample for Switch \d+ lcore \d+:", sample)

        # Splitting on each port
        port_samples = re.split("####", sample)




        # Loop through each entry. Which are stats for each port
        for port_sample in port_samples:
            # Skip empty entries
            if not port_sample.strip(): # Skip empty lines
                continue
            #print(port_sample)

            lines = port_sample.strip().split( "\n" )  # Split sample into lines
            port_info = lines[0].strip().split()  # Extract port information for first line that looks like : Second sample for Switch 0 port 21:
            switch = port_info[4]  # Extract switch number
            port = port_info[6]  # Extract port number
            port_data = {}  # Dictionary to store port data
            port_data['Sample']=index
            port_data['Port']=port

            for line in lines[1:]:
                if not line.strip():
                    continue # Skip empty lines
                key, value = line.strip().split()
                port_data[key] = int( value )

            # Putting to dictionary we just created in a dataframe (easier structure to use later)
            # Created data frame has a single colum with an autogenerated index
            df_port_data=pd.DataFrame.from_dict(port_data, orient='index')
            # Using temporary df to transpose data so now data is on one row with multiple colums indexed by sample and port
            temp_df = df_port_data.T
            temp_df.set_index(['Sample','Port'], inplace=True)

            # Create a DF with the difference between previous and current
            agg_df = pd.concat( [agg_df, temp_df] )


            #print("Port:" + port)
            print(port_data)

    diff_df = agg_df.groupby( 'Port' ).diff()
    # this gets only the final sample
    diff_df = diff_df.loc[diff_df.index.get_level_values( 'Sample' ).max()]

    import os
    filename_without_extension, file_extension = os.path.splitext( FILENAME )

    # Dumping to a csv file
    #print( f"Results saved to {filename_without_extension}.csv" )
    #non_zero_df.to_csv( filename_without_extension + ".csv", index=True )

    # Dunping to an excel file

    print( f"Results saved to {filename_without_extension}.xlsx" )

    diff_df.to_excel( filename_without_extension + ".xlsx" )
