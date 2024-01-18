export PYTHON_EXE_PATH="//Users/vcarlos/PycharmProjects/ensStats/venv"

# Function: Print a help message.
usage() { 
  echo "Usage: $0 [ -p File path ] [ -f filename.csv ] [-n hostname ] [-w workername]" 1>&2 

}
# Function: Exit with error.
exit_abnormal() {
  usage
  exit 1
}

while getopts p:f:n:w:h flag
do
    case "${flag}" in
        p) filepath=${OPTARG};;
        f) csvfile=${OPTARG};;
	n) host_name=${OPTARG};;
	w) worker_name=${OPTARG};;
        h) exit_abnormal
	;;
        *) exit_abnormal
	;;
    esac
done

# AllLcoreUsage.py		LcoreUsage.py			PCG_Drops.py			PerLcorevsPPS.py		TPUT_and_Packet_Drops.py	filter_eps.py			pervNICvsish.py
# CPU_and_Memory.py		Lcore_Assignment_Table.py	PerLcoreUsage.py		PerNicEps.py		filter_vsish.py			

if [ "$csvfile" = "" ]; then                 # If $NAME is an empty string,
  exit_abnormal
else                                      
 if [ -d "$filepath" ]; then
  echo "Path $filepath exists"
  file_path="$filepath/$csvfile"

  if [ -f "$file_path" ];then
	  echo "File $csvfile ($file_path) exits"
     echo "Executing scripts using  $filepath $csvfile $hostname and $worker_name"

     read -p "Per NIC EPS. Detects where on the run EPS are observed. Press any key to start ..."
     python3 $PYTHON_EXE_PATH/PerNicEps.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name | tee PerNicEps.txt

     read -p "EPS Analysis. Detects where on the run EPS are observed. Press any key to start ..."
     python3 $PYTHON_EXE_PATH/filter_eps.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name | tee filter_eps.txt

     read -p "per NIC vsish Analysis. Detects where on the run EPS are observed. Press any key to start ..."
     python3 $PYTHON_EXE_PATH/pervNICvsish.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name | tee pervNICvsish.txt

     read -p "vsish Analysis. Detects where on the run EPS are observed. Press any key to start ..."
     python3 $PYTHON_EXE_PATH/filter_vsish.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name | tee filter_vsish.txt

     read -p "Does a graph of usage on all lcores. Not very visually appealing. Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/AllLcoreUsage.py -p "$filepath" -f $csvfile -n $host_name | tee AllLcoreUsage.txt

     read -p "Does a CPU and Memory graph for a worker. Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/CPU_and_Memory.py -p "$filepath" -f $csvfile -w $worker_name  | tee CPU_and_Memory.txt

     read -p "Lcore assignment tables. Analyze changes on lcore allocation useful for when TLB is set to CPY Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/Lcore_Assignment_Table.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name  | tee Lcore_Assignment_table.txt

     read -p "Lcore Usage. Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/LcoreUsage.py -p "$filepath" -f $csvfile -n $host_name | tee LcoreUsage.txt

     read -p "PCG Drops. Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/PCG_Drops.py -p "$filepath" -f $csvfile -n $host_name -w $worker_name | tee PCG_Drops.txt

     read -p "Throughput . Press any key to continue ..."
     python3 $PYTHON_EXE_PATH/TPUT_and_Packet_Drops.py -p "$filepath" -f $csvfile | tee TPUT_and_Packet_Drops.txt

     read -p "Per Lcore Stats. Press any key to continue ..."
     while IFS= read -p "Enter Lcore Value (-1 to quit):" -r lcore
     do
	     if [ $lcore -eq -1 ]
	     then 
		     break
	     fi
	     python3 $PYTHON_EXE_PATH/PerLcoreUsage.py -p "$filepath" -f $csvfile -n $host_name -l $lcore | tee PerLcoreUsage_$lcore.txt
	     python3 $PYTHON_EXE_PATH/PerLcorevsPPS.py -p "$filepath" -f $csvfile -n $host_name -l $lcore | tee PerLcorevsPPS_$lcore.txt

     done




  else
	  echo "File $cvsfile"
	  echo "($file_path)"
	  echo "Does NOT exists"
  fi
 else
  echo "Path $filepath Does NOT exists"
 fi
fi
