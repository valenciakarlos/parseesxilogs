DURATION=60
ITERATIONS=10
PORTS_FILE=ports_file.txt
STATS_FILE=vsish_`date +"%d_%h_%T"`.txt

echo "Collecting stats for ports to $STATS_FILE"
nsxdp-cli ens port list | tee $PORTS_FILE
cat $PORTS_FILE > $STATS_FILE
CTR=1

while [ $ITERATIONS -gt 0 ]
do
        echo "{ Iteration number $CTR }" >> $STATS_FILE
        echo "Iteration number : $CTR"
        awk -f vsish.awk $PORTS_FILE >> $STATS_FILE
	ITERATIONS=$(( $ITERATIONS - 1 ))
	if [ $ITERATIONS -ne 0 ]
	then
		echo "Waiting $DURATION"
		sleep $DURATION
                CTR=$(( $CTR + 1 ))
	fi
done

echo "Resulting file $STATS_FILE"
egrep "UPLINK|VNIC|vsish|errors|Dropped|dropped" $STATS_FILE

