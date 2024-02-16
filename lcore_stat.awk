# Use together with flow_stats.sh or offline_flow_stats.sh
# For NSX-T 3.1.x calculates flow stats per lcore

BEGIN {
  print "-------------------"
  print "Parsing for lcore="lcore
  
}
# Print the headers
/^[a-zA-Z]/ {print $0}
# Match the requested lcore
$1~lcore { if (!($1 in arr)) {
		print $0; arr[$1]=$0
		}
	   else {
	        print $0 
	        split(arr[$1], org_arr) 
	        split ($0, curr_arr) 
	        for (i in curr_arr) { 
	            curr_arr[i]=curr_arr[i]-org_arr[i]
	        }
	   }
	}
	
END {
  print("Difference:")
  for (i in curr_arr)
  {
    printf(curr_arr[i]"\t ")
  }
  print("")
  hits=curr_arr[3]
  misses=curr_arr[4]
  localhits=curr_arr[6]
  totalhits=localhits+hits
  grandtotal=totalhits+misses
  print("Hits \t: "hits"\tLocal Hits \t:"localhits)
  print("Total Hits \t:"totalhits)
  print("Grand Total \t:"grandtotal)
  print("Misses\t\t:"misses)

  if (grandtotal!=0) {
    pct_hits=hits/grandtotal*100
    pct_misses=misses/grandtotal*100
  }
  else {
    pct_hits=0
    pct_misses=0
  }


  print("\t% of Hits:"pct_hits)
  print("\t% of Misses:"pct_misses)
  print "-------------------"
}

