#!/bin/bash
LANG=en_US.UTF-8
LANGUAGE=en
LC_CTYPE=en_US.UTF-8
for LIMIT in 5 2 1.5 1 0.8 0.6 0.4 0.2
do
    echo $LIMIT
    for CONNECTIONS in `seq 1 100`
    do
        echo "Number of connections: $CONNECTIONS"
        SECONDS=0
        for i in `seq 1 $CONNECTIONS`;
        do
            curl -w "%{time_total}\n" -o /dev/null -s https://cms.integreat-app.de/augsburg/de/wp-json/extensions/v3/pages/ &
        done
        wait
        echo $SECONDS
        #ERROR=$(bc <<< "$SECONDS>$LIMIT")
        #echo "$ERROR"
        #if [ "$ERROR" -gt "0" ]; then
        #    echo "Reation too slow with $CONNECTIONS and a limit of $LIMIT"
        #fi
    done
    echo ""
done
