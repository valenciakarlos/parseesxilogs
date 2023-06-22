Set of scripts to parse esxi stats generated with net-stats (json format) and sched-stats (text format) command.
To use these scripts ssh into an ESXi host and execute the following commands:
**************** COMMANDS TO RUN *****************************************
net-stats -i 120 -t WicQv -A > `hostname -s`_netstats.logs
sched-stats -t pcpu-stats > `hostname -s`_schedstats.logs

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

