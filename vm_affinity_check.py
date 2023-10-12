#!/usr/bin/env python3
import json
import sys
from prettytable import PrettyTable


# Deconstructing the json structure

if (len(sys.argv) != 3):
    print("Usage : vm_affinity_check.py <netstats_file> <sched_stats_file> ")
    exit()

def build_cpu_to_node_dict(sched_stats_file):
    # Using pandas to parse the sched stats file
    import pandas as pd
    df = pd.read_table(sched_stats_file, sep='\s+')
    # Exstracting the non-zero CPUs
    cpu_to_node_dict= {}
    # Threads
    table_sched = PrettyTable(['Cpu', 'Node', 'Thread'])
    print("Scheduler stats")
    for idx, thread in enumerate(df.exclusiveTo):
        if not (thread == 0):
            # Store info on dict with key being the thread id
            # print("Index=" + str(idx) + " Thread=" + str(thread) + " CPU=" + str(df.cpu[idx]) + " Node=" + str(df.node[idx]))
            table_sched.add_row([str(df.cpu[idx]), str(df.node[idx]), thread])
            used_pct=df.usedsec[idx]/df.elapsedsec[idx]
            cpu_to_node_dict[thread] = {'cpu': str(df.cpu[idx]), 'node': str(df.node[idx]), 'usedsec':df.usedsec[idx], 'elapsedsec':df.elapsedsec[idx],'idlesec':df.idlesec[idx],'used_pct':used_pct}

    #    print(table_sched)
    return cpu_to_node_dict

# Reference: https://realpython.com/python-pretty-print/
def main():
    # Open schedule stats file (second argument)
    sched_stats_file = sys.argv[2]
    # Open netstats file (first argument)
    netstats_file = sys.argv[1]

    print("Opening files " + sched_stats_file + " and " + netstats_file)
    schd_f = open(sched_stats_file)
    net_f = open(netstats_file)

    theJSON = json.load(net_f)
    thread_dict=build_cpu_to_node_dict(sched_stats_file)

    #print("Json Stats depth=2")
    #pprint(theJSON['stats'][0], depth=2)

    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            print("Name:"+port["name"])
            ''' Some debug dumping the whole set of keys on this port 
            print("Name:"+port["name"]+" Keys: ",end="")
            print(port.keys())
            '''
            # We can map sys to the sys dictionary that has all the threads associated to a name.
            if "sys" in port:
                print("\tSys:", end="")
                print(port["sys"])
                for thread in port["sys"]:
                    # Here we try to map this thread to an entry on the scheduler stats

                    # and print all the gathered information
                    try:
                        mappedCpu=thread_dict[int(thread)]["cpu"]
                        mappedNode=thread_dict[int(thread)]["node"]

                    except KeyError:
                        mappedNode = "NA"
                        mappedCpu="NA"

                    print("\t\tSys: " +thread +" Mapped Cpu: "+ mappedCpu +" Mapped Node: "+ mappedNode +" Name: ", end="")

                    if "lcoreusage" in stat['sys'][thread]:
                        print(stat['sys'][thread]['name'], end="")
                        print(" Lcore Usage:" + str(stat['sys'][thread]['lcoreusage']))
                    else:
                        print(stat['sys'][thread]['name'])

            if "vcpu" in port:
                print("\tVcpu:", end="")
                print(port["vcpu"])
                for thread in port["vcpu"]:
                    try:
                        mappedCpu=thread_dict[int(thread)]["cpu"]
                        mappedNode=thread_dict[int(thread)]["node"]

                    except KeyError:
                        mappedNode = "NA"
                        mappedCpu="NA"

                    print("\t\tVcpu: " + thread +" Mapped Cpu: "+ mappedCpu +" Mapped Node: "+ mappedNode + " Name: ", end="")
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
