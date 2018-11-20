#!/bin/bash
LANG=en_US.UTF-8
LANGUAGE=en
LC_CTYPE=en_US.UTF-8
LOCATIONS="augsburg regensburg nuernberg ahaus werne konstanz bochum fellbach kissing rheinberg rosenheim"
DOMAINS="cms.integreat-app.de"
for DOM in $DOMAINS; do
        for i in $(seq 1 100); do
                for LOC in $LOCATIONS; do
                        TIMING=$(curl -w "%{time_total}\n" -o /dev/null -s https://$DOM/$LOC/de/wp-json/extensions/v3/pages/)
                        echo "$DOM $LOC $TIMING"
                done
        done
done
