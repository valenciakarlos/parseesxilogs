import paramiko
import argparse
import difflib
import os
import time

import re

'''
Performs SSH to a server and does a diff between samples of the same command
Output must look like for it to work:
ctr: value

'''

integer_regex = r'^[+-]?\d+$'


def validate_arguments():
    parser = argparse.ArgumentParser (
        description="SSH to a host and runs a command displaying difference between samples" )
    # The first argument, input_file, is a positional argument (required).
    parser.add_argument ( "hostname", help="Hostname to check" )
    parser.add_argument ( "-u", "--username", help="User", default="ubuntu" )
    parser.add_argument ( "-p", "--password", help="Root password", default="NFV@solutioneng1!" )
    parser.add_argument ( "-i", "--iterations", type=int, help="Number if Iterations", default=2 )
    parser.add_argument ( "-t", "--time", type=int, help="Duration of each iteration", default=5 )
    parser.add_argument ( "-c", "--command", type=str, help="Command to execute:" )
    parser.add_argument ("-d", "--diff", help="Calculate difference (otherwise it just highlights" )
    parser.add_argument ( "-r", "--rate", help="`Calculate rate increase", default=0 )

    args = parser.parse_args ()
    return args


# MAIN BEGIN
# Validate arguments

args = validate_arguments ()
HOSTNAME = args.hostname
USERNAME = args.username
PASSWORD = args.password
COMMAND = args.command
ITERATIONS = args.iterations
DURATION = args.time

# Connect to the remote server
ssh = paramiko.SSHClient ()
ssh.set_missing_host_key_policy ( paramiko.AutoAddPolicy () )
ssh.connect ( HOSTNAME, port='22', username=USERNAME, password=PASSWORD )

# Caveat: Doesnt handle scroll well
# Cant do tables with multiple values at the moment


curr_output = ""
prev_output = ""
# Clear the screen
os.system ( 'cls' if os.name == 'nt' else 'clear' )

for ctr in range ( 1, ITERATIONS + 1 ):
    if args.rate:
        print ( "Rate increase selected. Running iteration : " + str ( ctr ) )
    else:
        print ( "Running iteration : " + str ( ctr ) )
    # Execute a command on the remote server
    stdin, stdout, stderr = ssh.exec_command ( COMMAND )

    curr_output = stdout.read ().decode ()
    # print(stdout.read().decode())
    # print(curr_output)
    # Check if this is not the first pass
    if (prev_output == ""):
        first_output = curr_output
        prev_output = curr_output
        print ( curr_output )

    else:
        # Not the 1st pass let's compare the results
        # Split the outputs into lists of lines
        lines2 = curr_output.strip ().split ( '\n' )
        lines1 = prev_output.strip ().split ( '\n' )
        prev_output = curr_output
        # Generate the diff of the two outputs
        differ = difflib.Differ ()
        diff = list ( differ.compare ( lines1, lines2 ) )
        matcher = difflib.SequenceMatcher ( None, lines1, lines2 )
        # Print the diff

        #print ( "This is the diff output:" )
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

        for tag, i1, i2, j1, j2 in matcher.get_opcodes ():
            # print(tag)
            if tag == 'equal':
                # print(f"equal {lines2[j1:j2]}")
                equal_lines = lines1[i1:i2]
                print ( '\n'.join ( equal_lines ) )
                # print(f"{lines2[j1:j2]}\n")

            if tag == 'replace':
                # It could be that several lines are different. If we want to get more details we need to process line by line
                diff_lines = lines2[j1:j2]
                # print(f"\033[43m{lines2[j1:j2]}\033[0m")
                org_lines = lines1[i1:i2]
                # print('\n'.join(org_lines))
                # If diff flag is set the differences will be calculated and displayed as highlight. Otherwise only highlight
                if (args.diff):
                    # diff flag was set
                    index = 0
                    # This only works on files for the type: "attrib: value"
                    while index < len ( diff_lines ):
                        # print('Original: \t'+org_lines[index])
                        # print('New: \t\t'+ diff_lines[index])
                        # Not sure why -1 is used on the array. 0 should be var name and 1 the value but -1 works
                        org_counter = org_lines[index].split ( ':' )[0]
                        diff_counter = diff_lines[index].split ( ':' )[0]
                        org_value = int ( org_lines[index].split ( ':' )[-1].strip () )
                        diff_value = int ( diff_lines[index].split ( ':' )[-1].strip () )
                        if (org_counter == diff_counter):
                            # If rate increase was selected obtain the percentage difference otherwise just show the difference
                            if (args.rate):
                                diff_rate= (diff_value - org_value) / DURATION
                                print ( '\033[33m' + org_counter + ": " + str ( diff_rate ) + '\033[0m' )
                            else:
                                print ( '\033[33m' + org_counter + ": " + str ( diff_value - org_value ) + '\033[0m' )
                        index += 1

                else:
                    print ( '\033[33m' + '\n'.join ( diff_lines ) + '\033[0m' )


    if (ctr != ITERATIONS):
        print ( "Sleeping for (seconds):" + str ( DURATION ) )
        time.sleep ( DURATION )
        os.system ( 'cls' if os.name == 'nt' else 'clear' )
    else:
        print ( "Final Iteration. Calculating totals" )
        print ( "First Run Numbers:" )
        print ( first_output )
        print ( "Last Run Numbers:" )
        print(curr_output)

        lines2 = curr_output.strip ().split ( '\n' )
        lines1 = first_output.strip ().split ( '\n' )

        # Generate the diff of the two outputs
        differ = difflib.Differ ()
        diff = list ( differ.compare ( lines1, lines2 ) )
        matcher = difflib.SequenceMatcher ( None, lines1, lines2 )

        for tag, i1, i2, j1, j2 in matcher.get_opcodes ():
            # print(tag)
            if tag == 'equal':
                # print(f"equal {lines2[j1:j2]}")
                equal_lines = lines1[i1:i2]
                print ( '\n'.join ( equal_lines ) )
                # print(f"{lines2[j1:j2]}\n")

            if tag == 'replace':
                # It could be that several lines are different. If we want to get more details we need to process line by line
                diff_lines = lines2[j1:j2]
                # print(f"\033[43m{lines2[j1:j2]}\033[0m")
                org_lines = lines1[i1:i2]
                # print('\n'.join(org_lines))
                if (args.diff):
                    # Print the difference with highlight
                    index=0
                    while index < len ( diff_lines ):
                        # print('Original: \t'+org_lines[index])
                        # print('New: \t\t'+ diff_lines[index])
                        # Not sure why -1 is used on the array. 0 should be var name and 1 the value but -1 works
                        org_counter = org_lines[index].split ( ':' )[0]
                        diff_counter = diff_lines[index].split ( ':' )[0]
                        org_value = int ( org_lines[index].split ( ':' )[-1].strip () )
                        diff_value = int ( diff_lines[index].split ( ':' )[-1].strip () )
                        if (org_counter == diff_counter):
                            if (args.rate):
                                diff_rate= (diff_value - org_value) / DURATION
                                print ( '\033[33m' + org_counter + ": " + str ( diff_rate ) + '\033[0m' )
                            else:
                                print ( '\033[33m' + org_counter + ": " + str ( diff_value - org_value ) + '\033[0m' )
                        index += 1
                else:
                    # Only highlight
                    print ( '\033[33m' + '\n'.join ( diff_lines ) + '\033[0m' )



# Close the SSH connection
time.sleep ( 2 )
ssh.close ()
