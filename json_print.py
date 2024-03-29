#!/usr/bin/env python3
import json
import sys
from pprint import pprint

# Deconstructing the json structure

if (len(sys.argv) == 1):
    print("Please enter JSON file file to parse")
    exit()

# Reference: https://realpython.com/python-pretty-print/
def main():
    if (len(sys.argv) == 1):
        print("Trying to locate local file netstats-logs")
        f = open("netstats-logs")
    else:
        print("Opening file " + sys.argv[1])
        f = open(sys.argv[1])

    theJSON = json.load(f)
    #print("Whole JSON structure:")
    #pprint(theJSON, depth=1)

    #print("Json Stats depth=2")
    #pprint(theJSON['stats'][0], depth=2)
    # Re to match the occurrence of a VM eth interface
    import re


    VNIC_PATTERN= r'^.+eth\d+$'

    VMS_DICT={}
    port_list=[]
    LCORE_PATTERN= r'^Ens-Lcore-(?P<lcore>\d)+$'




    for stat in theJSON["stats"]:
        for port in stat["ports"]:

            match = re.match(VNIC_PATTERN, port["name"])

            if match:
                #print("Found a vNIC :"+port["name"])
                vmname=re.split(r'[.]', port["name"])[0]
                #print(vmname)
                if vmname not in VMS_DICT:
                    port_list=[]
                    VMS_DICT[vmname]=port_list

                VMS_DICT[vmname].append(port)

            #print("Name:" + port["name"] + " Keys: ", end="")

            #print(port.keys())
            # We can map sys to the sys dictionary that has all the threads associated to a name.
            '''
            if "sys" in port:
                print("\tSys:", end="")
                print(port["sys"])
                for thread in port["sys"]:
                    print("\t\tSys: " +thread +" Name: ", end="")

                    if "lcoreusage" in stat['sys'][thread]:
                        print(stat['sys'][thread]['name'], end="")
                        print(" Lcore Usage:" + str(stat['sys'][thread]['lcoreusage']))
                    else:
                        print(stat['sys'][thread]['name'])

            if "vcpu" in port:
                print("\tVcpu:", end="")
                print(port["vcpu"])
                for thread in port["vcpu"]:
                    print("\t\tVcpu: " + thread + " Name: ", end="")
                    print(stat['vcpus'][thread]['name'])
            if "lcore" in port:
                print("\tLcore:",end="")
                print(port["lcore"])
            '''

    #print(VMS_DICT.keys())
    for vm in VMS_DICT.keys():
        print("Checking VM: "+vm)
        # Each vm has a list of ports
        for port in VMS_DICT[vm]:
            print ("\tChecking port :", end="")
            print(port["name"])
            print("\t\tLcores:",end="")
            if "lcore" in port:
                print(port["lcore"])
            else:
                print("No mapped lcores")
            # Print vCPUs. Really no need here as this repeats for each port. Figure out how to present this later. 
            '''
            for thread in port["vcpu"]:
                print("\t\tVcpu: " + thread + " Name: ", end="")
                thread_name=stat['vcpus'][thread]['name']
                print(thread_name)
            '''



            for thread in port["sys"]:
                print("\t\tSys: " + thread + " Name: ", end="")
                thread_name = stat['sys'][thread]['name']

                match_lcore = re.search(LCORE_PATTERN, thread_name)
                if (match_lcore):
                    lcore_id = match_lcore.group('lcore')

                # Check usage for the lcore

                if "lcoreusage" in stat['sys'][thread]:
                    print(stat['sys'][thread]['name'], end="")
                    print(" Lcore Usage:" + str(stat['sys'][thread]['lcoreusage']))
                else:
                    print(stat['sys'][thread]['name'])

                # Check direction for the lcore



'''
    new_table = PrettyTable()
    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            print(port.keys())
            for key in port.keys():
                if key not in new_table.field_names:
                    new_table.add_column(key, [])

    print(new_table)
    # Table has an attribute called field_names
    print(new_table.field_names)
    
Each VM port has a few interesting dictionaries:

port each port assigned to the VM.
sys are the thread allocated to tx and rx
vcpus are the actual CPUs allocate dto the VM. They are the same for all the ports. We want to validate that those vcpus have latency sensitivity
lcores are the ENS lcores assiged to the port.

{"name": "FGVM-TIGER-15-31.eth1", "switch": "DvsPortset-0", "id": 67108889, "mac": "00:50:56:bc:03:f1", "rxmode": 0, "tunemode": 0, "uplink": "false", "ens": "true", "promisc": "false", "sink": "false" ,
  "vnic": { "type": "vmxnet3", "ring1sz": 4096, "ring2sz": 4096, "tsopct": 0.0, "tsotputpct": 0.0, "txucastpct": 100.0, "txeps": 0.0,
  "sys": [ "2103448", "2101791", "2101801" ],
  "vcpu": [ "2103778", "2103780", "2103781" ],
  "lcore": [{"in": ["4", "4"],
             "out": ["12", "12"]}]},
{"name": "FGVM-TIGER-15-31.eth2", "switch": "DvsPortset-0", "id": 67108890, "mac": "00:50:56:bc:ec:16", "rxmode": 0, "tunemode": 0, "uplink": "false", "ens": "true", "promisc": "false", "sink": "false" ,
  "sys": [ "2103448", "2101790", "2101800" ],
  "vcpu": [ "2103778", "2103780", "2103781" ],
  "lcore": [{"in": ["3", "3"],
             "out": ["11", "11"]}]},

sys and lcore exists for vmnic too but not vcpu as that is only pertinent to VMs
'''

if __name__ == "__main__":
    main()
