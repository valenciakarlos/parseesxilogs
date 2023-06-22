BEGIN {
}

/^[0-9]+/ {
	    print "-------------------------"
            print $1" "$7
	    print "-------------------------"
            # Print all commands for PNIC related
            pnic_stats_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/pnicStats"
            print pnic_stats_cmd
            system(pnic_stats_cmd)

            input_stats_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/inputStats"
            print input_stats_cmd
            system(input_stats_cmd)

            output_stats_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/outputStats"
            print output_stats_cmd
            system(output_stats_cmd)

            stats_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/stats"
            print stats_cmd
            system(stats_cmd)

            status_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/status"
            print status_cmd
            system(status_cmd)
	    
            if ($7=="VNIC") {
                net3_rxsum_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/vmxnet3/rxSummary"
                print net3_rxsum_cmd
                system(net3_rxsum_cmd)
                net3_txsum_cmd="vsish -e get /net/portsets/DvsPortset-3/ports/"$1"/vmxnet3/txSummary"
                print(net3_txsum_cmd)
                system(net3_txsum_cmd)
                }
           }
          
END {
}
