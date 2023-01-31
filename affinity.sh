usage() {                                 # Function: Print a help message.
  echo "Usage: $0 [ -n netstats ] [ -s schedstats ]" 1>&2 
}
exit_abnormal() {                         # Function: Exit with error.
  usage
  exit 1
}

while getopts n:s:h flag
do
    case "${flag}" in
        n) netstat=${OPTARG};;
        s) schedstat=${OPTARG};;
        h) exit_abnormal
	;;
        *) exit_abnormal
	;;
    esac
done

# #check_drops.py		check_txrx_threads.py	exclaff.py		mbb_stats		nic_inv.py		nic_stats.py		sysstats.py		vcpus.py		

if [ "$netstat" = "" ]; then                 # If $NAME is an empty string,
  exit_abnormal
else                                      
 if [ -f "$netstat" ]; then
  echo "Executing scripts that use $netstat"
echo "--------------------- Sys stats -------------------------------"
  python3 sysstats.py $netstat
  echo "--------------------- CPU Stats -------------------------------"
  python3 vcpus.py $netstat
 if [ -f "$schedstat" ];then
     echo "Executing scripts that use $schedstat"
     echo "--------------------- Exclussive Affinity -------------------------------"
     python3 exclaff.py $netstat $schedstat

  else
     echo "$schedstat file not specified or does not exists"
  fi
 else
  echo "$netstat file does not exists"
 fi
fi
