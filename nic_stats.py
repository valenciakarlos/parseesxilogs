import json
import sys

import prettytable
from prettytable import PrettyTable
import pandas as pd


if (len(sys.argv)==1):
   print("Please enter file netstats file to parse")
   exit()

def main():
 if (len(sys.argv)==1):
    print("Trying to locate local file netstats-logs")
    f=open("netstats-logs")
 else:
    print("Opening file " + sys.argv[1])
    f=open(sys.argv[1])
 theJSON=json.load(f)
 if "hostname" in theJSON["sysinfo"]:
    print("Stats for " + theJSON["sysinfo"]["hostname"] + " pps=Packets Per Second")
    for stat in theJSON["stats"]:
        print("Iteration Number=" + str(stat["iteration"]))
        table = PrettyTable(['Port','switch','txpps','txeps','txmbps','txsize','txq_cnt','rxpps','rxeps','rxmbps','rxsize','rxq_cnt'])

    for port in stat["ports"]:
        if "txqueue" in port:
           txq_cnt=port["txqueue"]["count"]
        else:
           txq_cnt="NA"
        if "rxqueue" in port:
           rxq_cnt=port["rxqueue"]["count"]
        else:
           rxq_cnt="NA"
        table.add_row([port["name"],port["switch"],port["txpps"],port["txeps"],port["txmbps"],port["txsize"],txq_cnt,port["rxpps"],port["rxeps"],port["rxmbps"],port["rxsize"],rxq_cnt])

    # This format adds a couple of spaces at the begining of the number and set one decimal pint
    #table.float_format='2.1'
    table.float_format='2.1'
    from prettytable import MSWORD_FRIENDLY
    table.set_style(MSWORD_FRIENDLY)

    print(table)

    # Trying to create a more automatic table




    new_table=PrettyTable()
    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            #print(port.keys())
            for key in port.keys():
                if key not in new_table.field_names:
                    new_table.add_column(key,[])
            if "vmnic" in port:
                print("VMNIC:")
                print(port["vmnic"])
            if "vnic" in port:
                print("vnic:")
                print(port["vnic"])


    print("New automatic table (all values automatically added):")
    print(new_table)
    # Table has an attribute called field_names
    #print(new_table.field_names)
'''
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'intr', 'vmnic', 'txqueue', 'rxqueue', 'sys', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'intr', 'vmnic', 'txqueue', 'rxqueue', 'sys', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'intr', 'vmnic', 'txqueue', 'rxqueue', 'sys', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'intr', 'vmnic', 'txqueue', 'rxqueue', 'sys', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps', 'coalesce', 'vnic', 'rxqueue', 'txqueue', 'intr', 'sys', 'vcpu', 'lcore'])
dict_keys(['name', 'switch', 'id', 'mac', 'rxmode', 'tunemode', 'uplink', 'ens', 'promisc', 'sink', 'txpps', 'txmbps', 'txsize', 'txeps', 'rxpps', 'rxmbps', 'rxsize', 'rxeps'])

+------+--------+----+-----+--------+----------+--------+-----+---------+------+-------+--------+--------+-------+-------+--------+--------+-------+------+-------+---------+---------+-----+-------+----------+------+------+
| name | switch | id | mac | rxmode | tunemode | uplink | ens | promisc | sink | txpps | txmbps | txsize | txeps | rxpps | rxmbps | rxsize | rxeps | intr | vmnic | txqueue | rxqueue | sys | lcore | coalesce | vnic | vcpu |
+------+--------+----+-----+--------+----------+--------+-----+---------+------+-------+--------+--------+-------+-------+--------+--------+-------+------+-------+---------+---------+-----+-------+----------+------+------+
+------+--------+----+-----+--------+----------+--------+-----+---------+------+-------+--------+--------+-------+-------+--------+--------+-------+------+-------+---------+---------+-----+-------+----------+------+------+

    '''


if __name__ == "__main__":
  main()
 
