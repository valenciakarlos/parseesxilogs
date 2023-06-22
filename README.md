Set of scripts to parse esxi stats generated with net-stats (json format) and sched-stats (text format) command.
To use these scripts ssh into an ESXi host and execute the following commands:

net-stats -i 120 -t WicQv -A > `hostname -s`_netstats.logs


sched-stats -t pcpu-stats > `hostname -s`_schedstats.logs


Recommended script by Sorin:

net-stats -i $DUR1 -t WicQvE -S $switch
WicQvE
W : world stats for the tx, vmnic/vmknic worlds
i : Interrupt stats: Only for vmnics
c : Coalesce Stats: Only for vnics
Q : Detailed Queue stats for the port/nic
v : virtual nic stats
E : Enable stats collection for ENS module

Some others I could add: (*) Done (?) Candidate
         -d <level>         : verbose/debug level
         -V <vmname>        : VM name                                                               (**)
                 Find switches that contains the VM's ports. Print stats for VM's ports and uplinks

                 c : Coalesce Stats: Only for vnics                     
                 i : Interrupt stats: Only for vmnics                   (*)         
                 h : Cluster and Packet size histograms                 
                 v : virtual nic stats                                  (*)
                 e : Detailed error stats                         (?)      
                 q : Queue Stats for port/nic                     (?)      
                 Q : Detailed Queue stats for the port/nic              (*)
                 f : Detailed Queue filter information for port/nic (?)
                 W : world stats for the tx, vmnic/vmknic worlds        (*)
                 V : vcpu histograms                                (?)
                 S : System time breakdown by pcpus                 (?)
                 n : NIOC stats                                     
                 p : Passthru/sriov stats
                 P : Detailed sriov/passthru stats
                 E : Enable stats collection for ENS module             (*)
                     For ENS lcore stats:
                         lcore in  : vnic tx/pnic rx
                         lcore out : vnic rx/pnic tx
                 I : IOChain InputFilters stats
                 O : IOChain OutputFilters stats

Once collected, stats can be analyzed using:

python ~/parseesxilogs/nic_inv.py <netstats_file>
Will present a list of all pNICs and vNICs with stats as well as threads associated with each NIC.
Example:
carlos@ubuntu:~/test_results/Nov_24_07_09_6.5G_Drops$ python ~/parse_esxi_netstats/nic_inv.py resource-server31_netstats.logs
Arguments=2
Opening file resource-server31_netstats.logs
Stats for resource-server31
Iteration Number=0
+---------------+--------------+-------------------+--------+--------+--------+--------+
|      Port     |    switch    |        mac        | txpps  | txmbps | rxpps  | rxmbps |
+---------------+--------------+-------------------+--------+--------+--------+--------+
|     vmnic0    |   vSwitch0   | 24:6e:96:39:5e:4c |   14   |  0.0   |   11   |  0.0   |
|      vmk0     |   vSwitch0   | 24:6e:96:39:5e:4c |   14   |  0.0   |   10   |  0.0   |
|      vmk1     | DvsPortset-0 | 00:50:56:69:af:54 |   15   |  0.2   |   20   |  0.1   |
|      vmk2     | DvsPortset-0 | 00:50:56:66:3c:a5 |   0    |  0.0   |   0    |  0.0   |
|     vmnic7    | DvsPortset-0 | a0:36:9f:dc:91:b6 |   57   |  0.3   |   67   |  0.1   |
| SSM_75_5.eth0 | DvsPortset-0 | 00:50:56:9e:ed:91 |   42   |  0.1   |   41   |  0.1   |
| SSM_75_5.eth2 | DvsPortset-0 | 00:50:56:9e:1e:1f |   0    |  0.0   |   3    |  0.0   |
|     vmnic6    | DvsPortset-1 | a0:36:9f:dc:91:b4 | 423681 | 4562.4 | 105614 |  86.6  |
| SSM_75_5.eth3 | DvsPortset-1 | 00:50:56:9e:5b:a7 | 423680 | 4562.4 | 105614 |  86.6  |
|    vmnic10    | DvsPortset-8 | a0:36:9f:d7:0f:5c |   0    |  0.0   |   4    |  0.0   |
|    vmnic11    | DvsPortset-8 | a0:36:9f:d7:0f:5d |   0    |  0.0   |   4    |  0.0   |
|    vmnic12    | DvsPortset-9 | a0:36:9f:d7:0f:5e |   1    |  0.0   |   12   |  0.0   |
|      vmk3     | DvsPortset-9 | 00:50:56:66:92:b9 |   1    |  0.0   |   8    |  0.0   |
|     vmnic8    | DvsPortset-2 | a0:36:9f:dc:90:78 | 225418 | 119.9  | 308915 | 3237.6 |
| SSM_75_5.eth4 | DvsPortset-2 | 00:50:56:9e:01:06 | 225418 | 119.9  | 308915 | 3237.6 |
|     vmnic5    | DvsPortset-3 | a0:36:9f:dc:95:82 | 119379 | 1062.3 | 353962 | 2469.1 |
| SSM_75_5.eth1 | DvsPortset-3 | 00:50:56:9e:9d:57 | 119378 | 1062.3 | 353957 | 2469.1 |
+---------------+--------------+-------------------+--------+--------+--------+--------+
Threads associated with each NIC
Iteration Number=0
+---------------+----------+------------------------------+-------+---------+
|      Port     |  sys_id  |             name             |  used | exclaff |
+---------------+----------+------------------------------+-------+---------+
|     vmnic0    |  66249   | vmnic0-pollWorldnetpoll[00]  |  0.01 |    -1   |
|     vmnic0    |  66250   | vmnic0-pollWorldnetpoll[00]  |  0.01 |    -1   |
|     vmnic0    | 5298645  |         vmnic0-0-tx          |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|      vmk0     |  66689   |          vmk0-rx-0           |  0.0  |    -1   |
|      vmk0     |  66690   |           vmk0-tx            |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|      vmk1     |  66691   |          vmk1-rx-0           |  0.01 |    -1   |
|      vmk1     |  66692   |           vmk1-tx            |  0.01 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|      vmk2     |  66693   |          vmk2-rx-0           |  0.0  |    -1   |
|      vmk2     |  66694   |           vmk2-tx            |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|     vmnic7    |  66382   |      vmnic7-pollWorld-0      |  0.05 |    -1   |
|     vmnic7    |  66383   |      vmnic7-pollWorld-1      |  0.01 |    -1   |
|     vmnic7    |  66384   |   vmnic7-pollWorld-backup    |  0.0  |    -1   |
|     vmnic7    | 42552540 |         vmnic7-1-tx          |  0.0  |    -1   |
|     vmnic7    | 42552539 |         vmnic7-0-tx          |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
| SSM_75_5.eth0 | 43200587 |     NetWorld-VM-43200586     | 61.27 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
| SSM_75_5.eth2 | 43200587 |     NetWorld-VM-43200586     | 61.27 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|     vmnic6    |  66379   |      vmnic6-pollWorld-0      | 11.76 |    -1   |
|     vmnic6    |  66380   |      vmnic6-pollWorld-1      | 15.18 |    -1   |
|     vmnic6    |  66381   |   vmnic6-pollWorld-backup    |  0.0  |    -1   |
|     vmnic6    |  66712   |         vmnic6-0-tx          |  0.0  |    -1   |
|     vmnic6    |  66713   |         vmnic6-1-tx          |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
| SSM_75_5.eth3 | 43200587 |     NetWorld-VM-43200586     | 61.27 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|    vmnic10    |  66265   | vmnic10-pollWorldnetpoll[00] |  0.0  |    -1   |
|    vmnic10    |  66266   | vmnic10-pollWorldnetpoll[00] |  0.0  |    -1   |
|    vmnic10    |  66714   |         vmnic10-0-tx         |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|    vmnic11    |  66269   | vmnic11-pollWorldnetpoll[00] |  0.0  |    -1   |
|    vmnic11    |  66270   | vmnic11-pollWorldnetpoll[00] |  0.0  |    -1   |
|    vmnic11    |  66701   |         vmnic11-0-tx         |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|    vmnic12    |  66273   | vmnic12-pollWorldnetpoll[00] |  0.0  |    -1   |
|    vmnic12    |  66274   | vmnic12-pollWorldnetpoll[00] |  0.03 |    -1   |
|    vmnic12    |  66717   |      hclk-sched-vmnic12      |  0.0  |    -1   |
|    vmnic12    |  66718   |    hclk-watchdog-vmnic12     |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|      vmk3     |  66695   |          vmk3-rx-0           |  0.0  |    -1   |
|      vmk3     |  66696   |           vmk3-tx            |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|     vmnic8    |  66373   |      vmnic8-pollWorld-0      |  42.1 |    -1   |
|     vmnic8    |  66374   |      vmnic8-pollWorld-1      |  6.54 |    -1   |
|     vmnic8    |  66375   |   vmnic8-pollWorld-backup    |  0.0  |    -1   |
|     vmnic8    | 16034731 |         vmnic8-0-tx          |  0.0  |    -1   |
|     vmnic8    | 16034732 |         vmnic8-1-tx          |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
| SSM_75_5.eth4 | 43200587 |     NetWorld-VM-43200586     | 61.27 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
|     vmnic5    |  66370   |      vmnic5-pollWorld-0      | 37.29 |    -1   |
|     vmnic5    |  66371   |      vmnic5-pollWorld-1      |  4.71 |    -1   |
|     vmnic5    |  66372   |   vmnic5-pollWorld-backup    |  0.0  |    -1   |
|     vmnic5    |  66704   |         vmnic5-0-tx          |  0.0  |    -1   |
|     vmnic5    |  66705   |         vmnic5-1-tx          |  0.0  |    -1   |
|       --      |    --    |              --              |   --  |    --   |
| SSM_75_5.eth1 | 43200587 |     NetWorld-VM-43200586     | 61.27 |    -1   |
|       --      |    --    |              --              |   --  |    --   |
+---------------+----------+------------------------------+-------+---------+


Help for each command:

net-stats:

[root@telco-res-esx-1:~] net-stats --help
Usage:
         -l                 : List ports in system
         -a                 : Print absolute counts instead of per second counts
         -c <start>:<end>   : specify vsi-cache files instead of live kernel
         -d <level>         : verbose/debug level
         -f                 : ignore version check
         -h                 : this message
         -i <interval>      : Interval for stats collection (default=30 seconds)
         -n <iterations>    : number of iterations to run (default = 1)
         -o <outfile>       : output file

 Specify ports of interest as one of (Prioritized List of options)
         -A                 : Get stats for all ports on host
         -S <switchName>    : switch name
                 Lists stats for all non mgmt/test ports
         -N <pnicName>      : pnic name
                 List stats for all ports on switch that contains 'N'
         -V <vmname>        : VM name
                 Find switches that contains the VM's ports. Print stats for VM's ports and uplinks
         -s                 : Get storage world stats
         -I                 : Get SCSI and VSCSI storage I/O stats
         -D <name>          : Name of SCSI device/adapter/path or VM
                              To be used along with storage stat specs
                              Can be used multiple times
                              eg: net-stats -I -ta -D vmhba0 -D vmhba1
 OR specify port spec on command line
         -p <portid>        : portNum
         -t <type>          : specify a string with types of stats needed
 OR specify port spec in a config file
         -C <cfgFile>       : config file to read stats from
                 File Format: <portNum/switchName> <StatsSpec>

Stats Spec can contain one or more of these characters
                 c : Coalesce Stats: Only for vnics
                 i : Interrupt stats: Only for vmnics
                 h : Cluster and Packet size histograms
                 v : virtual nic stats
                 e : Detailed error stats
                 q : Queue Stats for port/nic
                 Q : Detailed Queue stats for the port/nic
                 f : Detailed Queue filter information for port/nic
                 W : world stats for the tx, vmnic/vmknic worlds
                 V : vcpu histograms
                 S : System time breakdown by pcpus
                 n : NIOC stats
                 p : Passthru/sriov stats
                 P : Detailed sriov/passthru stats
                 E : Enable stats collection for ENS module
                     For ENS lcore stats:
                         lcore in  : vnic tx/pnic rx
                         lcore out : vnic rx/pnic tx
                 I : IOChain InputFilters stats
                 O : IOChain OutputFilters stats
Stats Spec for Storage stats (-I)
                 d : SCSI Device Stats
                 a : SCSI Adapter Stats
                 t : SCSI Path Stats
                 s : VSCSI Stats

Note:
        net-stats reads multiple vsi nodes, one at a time, using system calls
        As data in the vsi nodes are continuously updated, there is going to
        be some inconsistency in numbers, hopefully, not a lot

         For ENS lcore stats:
                 lcore in  : vnic tx/pnic rx
                 lcore out : vnic rx/pnic tx


sched-stats:
[root@telco-res-esx-1:~] sched-stats --help
Usage:
         -c <file>   : use vsi-cache <file> instead of live kernel
         -t <type>   : specify the output type from the following list
                  :    vcpu-state-times
                  :    vcpu-run-times
                  :    vcpu-state-counts
                  :    vcpu-run-states
                  :    vcpu-alloc
                  :    vcpu-migration-stats
                  :    vcpu-load
                  :    vcpu-comminfo
                  :    vcpu-node-run-times
                  :    ncpus
                  :    cpu
                  :    pcpu-stats
                  :    pcpu-load
                  :    llc-load
                  :    qos-monitor
                  :    qos-enforcement
                  :    overhead-histo
                  :    sys-service-stats
                  :    run-state-histo
                  :    wait-state-histo
                  :    groups
                  :    power-pstates
                  :    power-cstates
                  :    numa-clients
                  :    numa-migration
                  :    numa-cnode
                  :    numa-pnode
                  :    numa-latency
         -f          : ignore version check
         -w          : only show stats of the specified world
         -g          : only show stats of the specified group
         -p          : only show stats of the specified pcpu
         -m          : only show stats of the specified module
         -r          : reset scheduler statistics
         -s <enable> : 1 to enable advanced cpu sched stats gathering, 0 to disable.
         -l <id>,<id> : comma separated list of ids to restrict the report to;
                        (not supported by all reports)
         -k          : check the correctness of scheduling stats
         -v          : verbose
         -q          : setting CSV Mode on
         -z          : Column selection filter
         -h          : print friendly help message

Note:
        Sched-stats reads the stats data from vmkernel for each vcpu one
        by one via the VSI interface. Since the scheduling stats may
        continue to change during the VSI calls, what's reported by
        sched-stats is not a consistent snapshot of the kernel stats.
        But the inconsistency is expected to be small.
