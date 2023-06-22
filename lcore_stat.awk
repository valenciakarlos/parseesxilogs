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
  #for (i in curr_arr) 
  #{
  #  printf(curr_arr[i]"\t ")
  #}
  hits=curr_arr[3]
  misses=curr_arr[4]
  pct_hits=hits/(hits+misses) 
  pct_misses=misses/(hits+misses) 
  print("Hits \t: "hits"\t% of Hits:"pct_hits)
  print("Misses\t: "misses"\t% of Misses:"pct_misses)
  print "-------------------"
}

