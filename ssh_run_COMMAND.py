# Executes ssh to a host and provides aggregate and per lcore stats 
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


# Executes a command we give either via command line or harcoded here (I know not pretty but I need this for now).
def validate_arguments():
    parser = argparse.ArgumentParser(description="SSH to a host and collects per lcore and aggregate flow stats")
    # The first argument, input_file, is a positional argument (required).
    parser.add_argument("hostname", help="Hostname to check")
    # For now will only do two iterations
    #parser.add_argument("-i", "--iterations", type=int, help="Number if Iterations", default=6)
    ##parser.add_argument("-d", "--duration", type=int, help="Duration of sleeps between iterations", default=5)
    parser.add_argument("-p", "--password", type=str, help="Password to connect to the servers", default="N294-admin")
    COMMAND="for vm in `vmdumper -l | grep -o 'cfgFile=\"[^\"]*[\"]' | cut -d'\"' -f2`; do echo -n 'Checking VM:'; echo $vm; egrep 'displayName|generatedAdd|ctx|rss|pnic|lat|smt|numvcpu|sched.cpu|cpuid|vvtd' $vm; done"
    parser.add_argument("-c", "--command", type=str, help="Command to execute:", default=COMMAND)

    args = parser.parse_args()
    return args

args = validate_arguments()
HOSTNAME = args.hostname
# Example n294-esxi-ht-01.sc.sero.gic.ericsson.se
PASSWORD = args.password
COMMAND  = args.command

# Connect to the remote server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOSTNAME,
            port='22', username='root', password=PASSWORD)

# Clear the screen
os.system('cls' if os.name == 'nt' else 'clear')
# Find the lcores I want to check
stdin, stdout, stderr = ssh.exec_command(COMMAND)
output=stdout.read().decode()
print(output)
# Close the SSH connection
time.sleep(2)
ssh.close()
