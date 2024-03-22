# Calculates flow stats
# Applicable to NSX-T and above only
import paramiko
import time
import difflib
import os
import json
import re
import json
import pandas as pd
import argparse
from prettytable import PrettyTable
import time
import math


def validate_arguments():
    parser = argparse.ArgumentParser(description="Calculates aggregate and per host flow stats")
    # The first argument, filename, is a positional argument (required).
    parser.add_argument("filename", help="Filename to parse")
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

''' Not needed anymore. Leaving as legacy as it does work

def calculate_ratios(lcore_idx, lcore_df):
    # Receives a dataframe with counter for an lcore and returns a dictionary with the ratios
    dict_ratios={}

    hits = lcore_df.loc[lcore_idx,'hits']
    miss = lcore_df.loc[lcore_idx,'miss']
    slowpath = lcore_df.loc[lcore_idx,'slowpath']
    localHits = lcore_df.loc[lcore_idx,'localHits']

    total_events = hits + miss + slowpath + localHits
    # dict_ratios['total_events']=total_events
    slowpath_ratio = slowpath / total_events
    dict_ratios['slowpath_ratio'] = slowpath_ratio
    hits_ratio = (hits + localHits) / total_events
    dict_ratios['hits_ratio'] = hits_ratio
    miss_ratio = miss / total_events
    dict_ratios['miss_ratio'] = miss_ratio
    hits_to_miss_ratio = (hits + localHits) / (hits + localHits + miss)
    dict_ratios['hits_to_miss_ratio'] = hits_to_miss_ratio
    miss_to_hits_ratio = miss / (hits + localHits + miss)
    dict_ratios['miss_to_hits_ratio'] = miss_to_hits_ratio
    print(f"Lcore={lcore_idx} Hits Ratio={hits_ratio:.2%} Slowpath ratio={slowpath_ratio:.2%} Miss ratio={miss_ratio:.2%} Hits to Miss ratio={hits_to_miss_ratio:.2%} Miss to Hits ratio={miss_to_hits_ratio:.2%} ")

    return dict_ratios
'''

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
        #print(f"Hits: '{hits}' Miss:'{miss}' Slowpath:'{slowpath}' localHits:'{localHits}' ")
        # To calcuate slowpath to hits ratio we divide the total of slowpath by the total of all packets (hits, miss, localhits and slowpath)
        # hits_ratio=(diff of hits + Diff of local hits) / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        # slowpath_ratio= slowpath / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        '''
        From Jin:
        
        We can categorize packets into 4 groups.
        1. Go to the slowpath without asking the flow table (counter: slowpath).
        2. Look up the local cache and it is a hit (counter: hits)
        3. Look up the real flow cache and it is a hit (counter: localHits)
        4. Look up the real flow cache and it is a miss (counter: miss).

        2 and 3 are disjointed. So the number of (total) flow hits = 2 + 3.

        We can have two different hit ratios.
        a. (2+3) / (1 + 2 + 3 + 4)
        b. (2+3) / (2 + 3 + 4)
        '''
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


# Checks if input_str is json formatted and returns a dictionary if it is. Otherwise it returns an empty dictionary
def is_json(input_str):
    dict={}
    try:
        dict=json.loads(input_str)
        return dict  # Dictionary will have some data
    except json.JSONDecodeError:
        return dict  # Dictionary would be empty

def find_number(string):
    # Extracts number for a like that looks like "string1: number string2"
    import re
    pattern = r'\b\d+\b'
    match=re.search(pattern,string)
    if match:
      return int(match.group())
    else:
       return 0

# Matcher to find integers

integer_regex = r'^[+-]?\d+$'

args = validate_arguments()
FILENAME = args.filename


# Here I need new logic to get stats for each lcore
import json

# Open the file containing the text
with open(FILENAME, "r") as file:
    # Read the contents of the file
    text = file.read()
    # Need to split this into multiple entries split at:
    # #### Second sample for Switch 0 lcore 1:
    samples= re.split("######################## Waiting \d+ seconds ########################", text)
    agg_df = pd.DataFrame()


    for index, sample in enumerate(samples):
        #print(sample)
        #json_entries = re.split("#### [First|Second] sample for Switch \d+ lcore \d+:", sample)

        json_entries = re.split("####", sample)


        # Loop through each JSON entry
        for entry in json_entries:
            # Skip empty entries
            if not entry.strip():
                continue

            # Extracting JSON part from the text
            json_part = entry[entry.find('{'):]


            # Parsing JSON into a dictionary
            data = json.loads(json_part)

            dict_curr_output = is_json(json_part)
            if dict_curr_output:
                #print("Output is json")
                dict_curr_output['Sample'] = index
                df_curr = pd.DataFrame.from_dict(dict_curr_output, orient='index')

                # Dataframe created with a single column (0) and the rows are all the entries on the sample for that lcore
                temp_df = df_curr
                # This transposes the DF so it now is one row (index autogenerated) with multiple colums
                temp_df = temp_df.T
                # This sets the indexes to be both sample and lcoreId
                temp_df.set_index( ['Sample','lcoreID'], inplace=True )
                # Create a DF with the difference between previous and current
                agg_df = pd.concat( [agg_df, temp_df] )



            else:
                print("Output is not JSON")
                break
        #print( "Sample Number:" + str( index ) )
    print( "Parsed stats (zero columns omitted)" )
    print( get_nonzero_df(agg_df).to_string( index=True ) )

    '''
    agg_df is indexed by sample and lcoreID ... all other attributes are in columns
    We use groupby('lcoreID') to group the DataFrame by 'lcoreID'.
    We apply the diff() function to calculate the difference between consecutive samples for each 'lcoreID'. This will result in NaN values for the first sample of each 'lcoreID'.
    The resulting DataFrame diff_df contains the difference in columns between samples per 'lcoreID'.
    
    '''

    diff_df = agg_df.groupby( 'lcoreID' ).diff()

    '''
    We use this to obtain the final sample
    diff_df.loc[diff_df.index.get_level_values('Sample').max()]
    '''

    diff_df=diff_df.loc[diff_df.index.get_level_values('Sample').max()]
    #print(diff_df)

    # print("Non Zero Diff DF")
    #non_zero_df = get_nonzero_df( agg_df ).copy()
    # I think it's the diff_df
    non_zero_df = get_nonzero_df( diff_df ).copy()
    # Apply the function calculate_ratios_vectorized and assign results to new columns in the copy
    #print("Non zeros DF:")
    #print(non_zero_df)




    # This part is still not working TBD


    # Apply the function calculate_ratios_vectorized and assign results to new columns in the copy axis=1 applies the function per rows
    non_zero_df.loc[:,['slowpath_ratio', 'hits_ratio', 'miss_ratio', 'hits_to_miss_ratio', 'miss_to_hits_ratio']] = non_zero_df.apply(calculate_ratios_vectorized, axis=1 )



    print("Final calculations")


    format_mapping = {'slowpath_ratio': "{:.1%}", 'hits_ratio': "{:.1%}", 'miss_ratio': "{:.1%}",'hits_to_miss_ratio': "{:.1%}", 'miss_to_hits_ratio': "{:.1%}"}


    non_zero_df.style.format( format_mapping )

    ''' 
    Examples of formats


    # Define different formats for each column
    column_formats = {
        'A': '{:,.2f}'.format,  # Format column A as float with two decimal places
        'B': '{:.2%}'.format,  # Format column B as percentage with two decimal places
        'C': '{:,.0f}'.format  # Format column C as integer with no decimal places
    }
    
    '''

    pd.set_option( 'display.float_format', '{:,.2f}'.format )
    # This works
    print( non_zero_df.to_string( index=True))
    # this does not

    #print( non_zero_df.to_string( index=False, formatters=format_mapping ) )

    import os
    filename_without_extension, file_extension = os.path.splitext( FILENAME )

    # Dumping to a csv file
    #print( f"Results saved to {filename_without_extension}.csv" )
    #non_zero_df.to_csv( filename_without_extension + ".csv", index=True )

    # Dunping to an excel file

    print( f"Results saved to {filename_without_extension}.xlsx" )
    non_zero_df.style.format( format_mapping ).to_excel( filename_without_extension + ".xlsx" )