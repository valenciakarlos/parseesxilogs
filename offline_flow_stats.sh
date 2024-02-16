export SCRIPT_PATH="/Users/vcarlos/PycharmProjects/parseesxilogs"
STATS_FILE=stats_flows.txt
ENS_FLOW_STATS=$1

echo "Parsing file $ENS_FLOW_STATS"
lcores=`cat $ENS_FLOW_STATS | grep "^\d" | awk '!seen[$1]++ {print $1}'`
HEADERS=`cat $ENS_FLOW_STATS | grep lcoreID | head -1`
echo $HEADERS
echo "$HEADERS" > $STATS_FILE

for lcore_id in $lcores
do
		STAT_LINE=`cat $ENS_FLOW_STATS | grep "^$lcore_id"`
		#echo "$STAT_LINE"
		echo "$STAT_LINE" >> $STATS_FILE
done

echo "------"
echo "Resulting file $STATS_FILE"
cat $STATS_FILE

for l in $lcores 
do 
	awk -v lcore=$l -f $SCRIPT_PATH/lcore_stat.awk $STATS_FILE
done

