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
  python3 $SCRIPT_PATH/nic_inv.py $netstat | tee nic_inv_$netstat
  echo "--------------------- Nic Stats -------------------------------"
  python3 $SCRIPT_PATH/nic_stats.py $netstat | tee nic_stats_$netstat
  echo "--------------------- check tx and rx threads -------------------------------"
  python3 $SCRIPT_PATH/check_txrx_threads.py $netstat | tee tx_rx_threads_$netstat
  echo "--------------------- Check for drops -------------------------------"
  python3 $SCRIPT_PATH/check_drops.py $netstat | tee check_drops_$netstat
  echo "--------------------- Sys stats -------------------------------"
  python3 $SCRIPT_PATH/sysstats.py $netstat| tee sys_stats_$netstat
  echo "--------------------- CPU Stats -------------------------------"
  python3 $SCRIPT_PATH/vcpus.py $netstat | tee vcpus_$netstat
  echo "--------------------- VM Stats -------------------------------"
  python3 $SCRIPT_PATH/vm_stats.py $netstat | tee vm_stats_$netstat
  echo "--------------------- VM Inventory -------------------------------"
  python3 $SCRIPT_PATH/json_print.py $netstat | tee vm_inv_$netstat

  if [ -f "$schedstat" ];then
     echo "Executing scripts that use $schedstat"
     echo "--------------------- Exclussive Affinity -------------------------------"
     python3 $SCRIPT_PATH/exclaff.py $netstat $schedstat | tee exclaff_$schedstat
     echo "---------------------  Affinity Checker -------------------------------"
     python3 $SCRIPT_PATH/affinity_check.py $netstat $schedstat | tee affinity_check_$schedstat


  else
     echo "$schedstat file with scheduler stats not specified or does not exists"
  fi
 else
  echo "$netstat file with net-stats does not exists"
 fi
fi
