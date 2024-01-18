import paramiko
import time
import difflib
import os
import json
import re
import json
import pandas as pd
import argparse


def validate_arguments():
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("-n", "--hostname", help="Hostname to check", required=True)
    args = parser.parse_args()
    return args

# Does some calculations if the DF has all the info we need
# Receives two data frames and provides the ratio of slow path to misses
def get_ratios(df_one,df_two):
    try:
        # Try to extract the value for the indexes we need
        hits=df_two.loc['hits',0]-df_one.loc['hits',0]
        miss=df_two.loc['miss',0]-df_one.loc['miss',0]
        slowpath=df_two.loc['slowpath',0]-df_one.loc['slowpath',0]
        localHits=df_two.loc['localHits',0]-df_one.loc['localHits',0]
        print("on the get slowpath ratio")
        print(f"Hits: '{hits}' Miss:'{miss}' Slowpath:'{slowpath}' localHits:'{localHits}' ")
        # To calcuate slowpath to hits ratio we divide the total of slowpath by the total of all packets (hits, miss, localhits and slowpath)
        # hits_ratio=(diff of hits + Diff of local hits) / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        # slowpath_ratio= slowpath / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        total_events=hits+miss+slowpath+localHits
        slowpath_ratio=slowpath/total_events
        hits_ratio=(hits+localHits)/total_events
        miss_ratio=miss/total_events
        hits_to_miss_ratio=(hits+localHits)/(hits+localHits+miss)
        miss_to_hits_ratio=miss/(hits+localHits+miss)
        print(f"Hits Ratio={hits_ratio:.2%} Slowpath ratio={slowpath_ratio:.2%} Miss ratio={miss_ratio:.2%} Hits to Miss ratio={hits_to_miss_ratio:.2%} Miss to Hits ratio={miss_to_hits_ratio:.2%} ")
    except KeyError:
        # Handle the case where the index does not exist
        print("Error could not extract some indexes")

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

# Connect to the remote server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('n294-esxi-ht-01.sc.sero.gic.ericsson.se',
            port='22', username='root', password='N294-admin')
# COMMAND='netstat -i'
# COMMAND='netstat -i| egrep "eno1|lo"'
# COMMAND='netstat -s | grep -A5 Tcp'
COMMAND = 'nsxdp-cli ens flow-stats get'
#COMMAND = 'nsxdp-cli ens flow-stats get -l 9'
#COMMAND = 'vsish -e get /net/portsets/DvsPortset-2/stats'

# Caveat: Doesnt handle scroll well

ITERATIONS = 6
DURATION = 10


curr_output = ""
prev_output = ""
# Clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

for ctr in range(1, ITERATIONS+1):
    print("Running iteration : " + str(ctr))
    # Execute a command on the remote server
    stdin, stdout, stderr = ssh.exec_command(COMMAND)

    curr_output = stdout.read().decode()
    dict_curr_output=is_json(curr_output)
    if dict_curr_output:
        df_curr=pd.DataFrame.from_dict(dict_curr_output, orient='index')
    else:
        print("Output is not JSON")

    # print(stdout.read().decode())
    print("Current Output is :")
    print(curr_output)
    # Check if this is not the first pass
    if (prev_output == ""):
        first_output = curr_output
        prev_output = curr_output

        df_first=df_curr # Dataframe with the very first readings
        df_b4=df_curr   # Store data of previous df
        #print(curr_output)

    else:
        # Not the 1st pass let's compare the results
        # Split the outputs into lists of lines
        lines2 = curr_output.strip().split('\n')
        lines1 = prev_output.strip().split('\n')
        prev_output = curr_output

        # Use df to calculate the difference
        diff_df=df_curr-df_b4
        print("Dataframe difference calculations")
        print(diff_df)
        get_ratios(df_b4, df_curr)

        df_b4=df_curr


        # Generate the diff of the two outputs
        differ = difflib.Differ()
        diff = list(differ.compare(lines1, lines2))
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        # Print the diff

        # print("This is the diff output:")
        # print('\n'.join(diff))
        # print('Diff:\n'.join(diff))
        # print('Running Matcher!')
        # This matcher will work for me. We just need to feed one line at a time. It shows exactly on the line where the change is

        ''' Matcher get_opcodes() is used to compare two sequences and identify the differences between them. i1,i2 are the index of the 1st sequence and j1,j2 of the second.
			tag the operation that needs to reflect the change
			Right now I am doing per line matching but I can get more granular (exact digits that changed) as I already have all the info
			The print at the bottom shows the different lines with a different color
			
			The possible values for the operation type are:

    		"equal": Indicates that the corresponding sequences are identical.

    		"delete": Indicates that the corresponding elements from the first sequence have been deleted.

    		"insert": Indicates that the corresponding elements have been inserted into the second sequence.

    		"replace": Indicates that the corresponding elements have been replaced by new elements in the second sequence.
    
    		Right now only equal and replace are implemented.
		'''

        # Below works well and matches on whole lines highlighting changes. But we want to be able to detect the changes. On maybe even clear the stats. Only way to do that would be to process line by and if we detect a number dump to a table for later comparison

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            # print(tag)
            if tag == 'equal':
                # print(f"equal {lines2[j1:j2]}")
                equal_lines = lines1[i1:i2]
                #print('\n'.join(equal_lines))
                #print(f"{lines2[j1:j2]}\n")

            if tag == 'replace':
                # It could be that several lines are different. If we want to get more details we need to process line by line
                diff_lines = lines2[j1:j2]
                #print(f"\033[43m{lines2[j1:j2]}\033[0m")
                org_lines = lines1[i1:i2]
                # print('\n'.join(org_lines))
                # Uncomment next two lines to display different lines with a highlight
                print("Differences:")
                print('\033[33m' + '\n'.join(diff_lines) + '\033[0m')   # Highlight differences
                index = 0
                while index < len(diff_lines):
                    #print('Original: \t'+org_lines[index])
                    #print('New: \t\t' + diff_lines[index])
                    # Not sure why -1 is used on the array. 0 should be var name and 1 the value but -1 works
                    # Need to match different
                    # Code below only works for counter: 1234
                    '''
					org_counter=org_lines[index].split(':')[0]
					diff_counter=diff_lines[index].split(':')[0]
					org_value = int(org_lines[index].split(':')[-1].strip())
					diff_value= int(diff_lines[index].split(':')[-1].strip())
					if (org_counter==diff_counter):
						print("Diff" +org_counter+ ": " + str(diff_value-org_value))
					'''
                    # Obtain counter names
                    org_counter=org_lines[index].split(':')[0]
                    diff_counter=diff_lines[index].split(':')[0]
                    if (org_counter==diff_counter):
                        # Define pattern. \b any word \d+ any integer \b any word
                        org_value=find_number(org_lines[index])
                        diff_value=find_number(diff_lines[index])
                        #print("Diff" +org_counter+ ": " + str(diff_value-org_value))




                    index += 1

                # Let's traverse each different line and find the difference in more detail (how to store so we can calculate difference?)

    """
	
	"""
    if (ctr != ITERATIONS):
        print("Sleeping for (seconds):" + str(DURATION))
        time.sleep(DURATION)
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print("Final Iteration. Calculating totals")
        print("First Run Numbers:")
        print(first_output)
        print("Last Run Numbers:")
        print(curr_output)

        lines2 = curr_output.strip().split('\n')
        lines1 = first_output.strip().split('\n')

        # Generate the diff of the two outputs
        differ = difflib.Differ()
        diff = list(differ.compare(lines1, lines2))
        matcher = difflib.SequenceMatcher(None, lines1, lines2)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            # print(tag)
            if tag == 'equal':
                # print(f"equal {lines2[j1:j2]}")
                equal_lines = lines1[i1:i2]
                # Uncoment below to display lines that are equal
                #print('\n'.join(equal_lines))
                # print(f"{lines2[j1:j2]}\n")

            if tag == 'replace':
                # It could be that several lines are different. If we want to get more details we need to process line by line
                diff_lines = lines2[j1:j2]
                # print(f"\033[43m{lines2[j1:j2]}\033[0m")
                org_lines = lines1[i1:i2]
                # print('\n'.join(org_lines))
                # Uncomment next two lines below to display the lines that are different
                print("Different lines:")
                print('\033[33m' + '\n'.join(diff_lines) + '\033[0m')
                index = 0
                while index < len(diff_lines):
                    # print('Original: \t'+org_lines[index])
                    # print('New: \t\t'+ diff_lines[index])
                    # Not sure why -1 is used on the array. 0 should be var name and 1 the value but -1 works
                    org_counter = org_lines[index].split(':')[0]
                    diff_counter = diff_lines[index].split(':')[0]
                    '''
                    org_value = int(org_lines[index].split(':')[-1].strip())
                    diff_value = int(diff_lines[index].split(':')[-1].strip())
                    '''
                    if (org_counter == diff_counter):
                        diff_value=find_number(diff_lines[index])
                        org_value=find_number(org_lines[index])
                        # Uncomment below if you want to display the diff
                        #print("Diff" + org_counter + ": " +
                              #str(diff_value-org_value))
                    index += 1


        # Calculate the difference based on first and last data frame

        agg_diff_df=df_curr-df_first
        print("Difference based on dataframes is:")
        print(agg_diff_df)
        get_ratios(df_first, df_curr)
# Close the SSH connection
time.sleep(2)
ssh.close()
