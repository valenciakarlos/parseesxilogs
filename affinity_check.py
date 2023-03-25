import json
import sys
from typing import Dict, Any

from prettytable import PrettyTable

if (len(sys.argv) != 3):
    print("Usage : exclaff.py <sched_stats_file> <netstats_file>")
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
            cpu_to_node_dict[thread] = {'cpu': str(df.cpu[idx]), 'node': str(df.node[idx])}

    #    print(table_sched)
    return cpu_to_node_dict

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

    # Traversing the cpu stats
    if "hostname" in theJSON["sysinfo"]:
        print("vCPU affinity info for " + theJSON["sysinfo"]["hostname"])
        for stat in theJSON["stats"]:
            print("Iteration Number=" + str(stat["iteration"]))
            #table = PrettyTable(['Name', 'Id', 'used', 'latencySensitivity', 'vcpu_exclaff'])
            # Table with threads allocated to the VMX Cpus
            vmx_cpu_thread_table = PrettyTable(['Name','Id','used','latencySensitivity','vcpu_exclaff','node'])
            # Tables for the system Threads including vmnics and Lcores
            sys_threads_table = PrettyTable(
                ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff'])
            sys_threads_table_exclaff = PrettyTable(
                ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff'])

            # Capturing and traversing the vcpus dictionary
            vcpus_dict = stat["vcpus"]

            for vcpuId, vcpu_attrib in vcpus_dict.items():  # Traversing a dictionary
                if "latencySensitivity" in vcpu_attrib:  # Some of the CPU stats dont have latency sensitivity and exclaff so need to validate for that
                    latSen = vcpu_attrib["latencySensitivity"]
                    exclaff = vcpu_attrib["exclaff"]
                else:
                    latSen = "NA"
                    exclaff = "NA"
                try:
                    mappedNode=(thread_dict[vcpu_attrib["id"]]["node"])
                except KeyError:
                    mappedNode="NA"
                vmx_cpu_thread_table.add_row([vcpu_attrib["name"], vcpu_attrib["id"], vcpu_attrib["used"], latSen, exclaff,mappedNode])
            print(vmx_cpu_thread_table)

            # Capture and traverse the sys dictionary which contains system threads
            sys_dict = stat["sys"]
            # Tables for the system Threads including vmnics and Lcores
            sys_threads_table = PrettyTable(
                ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff'])
            sys_threads_table_exclaff = PrettyTable(
                ['Port', 'Switch', 'Thread Id', 'Name', 'Usage', 'Ready', 'Cstp', 'latencySen', 'exclaff','node'])

            for port in stat["ports"]:
                if "sys" in port:
                    for thread in port["sys"]:
                        sys_threads_table.add_row(
                            [port["name"], port['switch'], thread, sys_dict[thread]["name"], sys_dict[thread]["used"],
                             sys_dict[thread]["ready"], sys_dict[thread]["cstp"],
                             sys_dict[thread]["latencySensitivity"], sys_dict[thread]["exclaff"]])
                        # Storing on the other table only of exclusive affinity exists
                        if not sys_dict[thread]["exclaff"] == -1:
                            try: # Try to find NUMA node mapping
                                mappedNode = (thread_dict[int(thread)]["node"])
                            except KeyError:
                                mappedNode = "NA"
                            sys_threads_table_exclaff.add_row([port["name"], port['switch'], thread, sys_dict[thread]["name"],
                                                   sys_dict[thread]["used"], sys_dict[thread]["ready"],
                                                   sys_dict[thread]["cstp"], sys_dict[thread]["latencySensitivity"],
                                                   sys_dict[thread]["exclaff"], mappedNode])
            #print(sys_threads_table)
            print("Entries with exclusive affinity on threads")
            print(sys_threads_table_exclaff)

if __name__ == "__main__":
    main()
