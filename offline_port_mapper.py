# Calculates per port stats
'''
Takes a nic_inv.csv file that has the portId and get the ensPID from the ens-port-info.txt file
#### ENS port list for Switch DvsPortset-1 ###

Something like this would do

egrep "^100663335" ens-port-info.txt

portID      ensPID TxQ RxQ hwMAC             numMACs  type         Queue Placement(tx|rx)
------------------------------------------------------------------------------
100663335   0      1   1   00:50:56:62:2f:72 0        GENERIC      6 |6

'''

import re
import pandas as pd
import argparse



def validate_arguments():
    parser = argparse.ArgumentParser(description="Calculates per port stats")
    # The first argument, filename, is a positional argument (required).
    parser.add_argument("filename", help="NIC Info CSV Filename to parse", default='nic_inv.csv')
    parser.add_argument( "-e", "--ensportinfo", type=str, help="Text file with ens port info ", default='ens-port-info.txt' )
    # File must have portID labeled as id
    # Might want to pass a file with the mapping of port name and switch name. see nic_inv.py for details
    # For now will only do two iterations
    args = parser.parse_args()
    return args

def extract_text_between_markers(file_path, start_marker, end_marker):
    '''
    Extracts text between defined markers
    :param file_path: file name to check
    :param start_marker: Start marker to match (can be a regular expression)
    :param end_marker:   End marker to match (can be a regular expression)
    :return: texto with info extracted
    Example here:


    #### ENS port list for Switch DvsPortset-1 ###

    portID      ensPID TxQ RxQ hwMAC             numMACs  type         Queue Placement(tx|rx)
    ------------------------------------------------------------------------------
    100663335   0      1   1   00:50:56:62:2f:72 0        GENERIC      6 |6
    100663336   1      1   1   00:50:56:6c:c9:50 0        GENERIC      0 |0
    100663337   2      1   1   00:50:56:6f:1d:48 0        GENERIC      0 |0
    100663338   3      1   1   00:50:56:62:6e:9b 0        GENERIC      0 |0
    100663339   4      1   1   00:50:56:6d:78:2e 0        GENERIC      0 |0
    2248146979  5      24  24  88:e9:a4:30:0f:f9 0        UPLINK       0 1 2 3 4 5 6 7 - - - - - - - - - - - - - - - - |0 0 0 0 0 1 2 3 4 5 6 7 - - - - - - - - - - - -
    2248146977  6      24  24  88:e9:a4:30:0f:d4 0        UPLINK       0 1 2 3 4 5 6 7 - - - - - - - - - - - - - - - - |6 6 6 6 0 1 2 3 4 5 6 7 - - - - - - - - - - - -
    2248146975  7      24  24  88:e9:a4:30:0f:d5 0        UPLINK       0 1 2 3 4 5 6 7 - - - - - - - - - - - - - - - - |7 7 7 7 0 1 2 3 4 5 6 7 - - - - - - - - - - - -
    2248146973  8      24  24  88:e9:a4:30:0f:f8 0        UPLINK       0 1 2 3 4 5 6 7 - - - - - - - - - - - - - - - - |0 0 0 0 0 1 2 3 4 5 6 7 - - - - - - - - - - - -
    100663368   9      8   8   00:50:56:a9:b7:39 0        VNIC         1 1 1 1 1 1 1 1 |1 1 1 1 1 1 1 1
    100663367   10     2   7   00:50:56:a9:87:c4 0        VNIC         3 1 |2 2 3 0 0 0 0
    100663366   11     2   7   00:50:56:a9:dc:f4 0        VNIC         2 1 |2 3 3 3 0 1 0
    100663365   12     2   7   00:50:56:a9:c5:a4 0        VNIC         2 3 |3 3 2 1 2 0 2
    ### TLB Configuration ###
    '''


    import re


    extracted_text = ""
    start_found = False
    with open ( file_path, 'r' ) as file:
        for line in file:
            if re.match(start_marker,line):
                start_found = True
                continue
            elif re.match(end_marker,line):
                if start_found:
                    break
            if start_found:
                extracted_text += line
    return extracted_text.strip ()

args = validate_arguments()
FILENAME = args.filename
ENS_PORT_INFO= args.ensportinfo

# The column name I was to search for
column_name = 'id'



print("Checking file "+FILENAME)
print("ENS Port Info "+ENS_PORT_INFO)

import pandas as pd


# Read the CSV file into a pandas DataFrame
df = pd.read_csv(FILENAME)
df.set_index(column_name, inplace=True)
print("Dataframe from csv file")
print(df)
#print(df[column_name])

'''
want the ens port info which is between 
#### ENS port list for Switch DvsPortset-1 ###
and
### TLB Configuration ###

'''

ens_port_info=extract_text_between_markers(ENS_PORT_INFO, "#### ENS port list for Switch DvsPortset-\d+ ###", "### TLB Configuration ###")
print("Text is:")
#print(ens_port_info)

# Regular expression to match portId and ensPID
# portID      ensPID TxQ RxQ hwMAC             numMACs  type         Queue Placement(tx|rx)
# ------------------------------------------------------------------------------
# 100663335   0      1   1   00:50:56:62:2f:72 0        GENERIC      6 |6

# and capture the value from the first (portID) and second column (ensPID)
pattern = re.compile(r'^(\d+)\s+(\d+)\s')


# Iterate over the lines and extract values from the first and second columns
portID_and_ensPID = [(match.group(1), match.group(2)) for line in ens_port_info.split('\n') if (match := re.match(pattern, line))]

# Convert the list of tuples to a dictionary
portID_and_ensPID_dict = dict(portID_and_ensPID)

#print(portID_and_ensPID_dict)


# Iterate over DataFrame row by row and add the ensPID
for index, row in df.iterrows():
    # Calculate value for new column
    print("Index is:", end="")
    print(type(index))
    if str(index) in portID_and_ensPID_dict:

      df.at[index,'ensPID']=int(portID_and_ensPID_dict[str(index)])  # adding the ensPID to the dataframe

#print(df)

import os

filename_without_extension, file_extension = os.path.splitext ( FILENAME )

# Dumping to a csv file
# print( f"Results saved to {filename_without_extension}.csv" )
# non_zero_df.to_csv( filename_without_extension + ".csv", index=True )

# Dunping to an excel file

print ( f"Results saved to {filename_without_extension}.xlsx" )

df.to_excel ( filename_without_extension + ".xlsx" )




