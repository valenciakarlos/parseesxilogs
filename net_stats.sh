export SCRIPT_PATH="/Users/vcarlos/PycharmProjects/parseesxilogs"

# Function: Print a help message.
usage() {
  echo "Usage: $0 [ -n netstats ] [ -s schedstats ]" 1>&2 
}

# Function: Exit with error.
exit_abnormal() {
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
  echo "--------------------- Nic Iventory -------------------------------"
  python3 $SCRIPT_PATH/nic_inv.py $netstat
  echo "--------------------- Nic Stats -------------------------------"
  python3 $SCRIPT_PATH/nic_stats.py $netstat
 echo "--------------------- Check for drops -------------------------------"
  python3 $SCRIPT_PATH/check_drops.py $netstat
 else
  echo "$netstat file does not exists"
 fi
fi