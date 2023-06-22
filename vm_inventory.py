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
    print("Whole JSON structure:")
    pprint(theJSON, depth=1)

    #print("Json Stats depth=2")
    #pprint(theJSON['stats'][0], depth=2)

    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            print("Name:"+port["name"]+" Keys: ",end="")
            print(port.keys())
            # We can map sys to the sys dictionary that has all the threads associated to a name.
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
