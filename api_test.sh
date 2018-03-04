#!/bin/bash
# This scipt tests if the API responds in a given time (LIMIT). If the
# response is to slow, admins are notified via e-mail. This script is
# suitable for cron jobs.
LANG=en_US.UTF-8
LANGUAGE=en
LC_CTYPE=en_US.UTF-8
TIMING=$(curl -w "%{time_total}\n" -o /dev/null -s https://cms.integreat-app.de/augsburg/de/wp-json/extensions/v3/pages/)
LIMIT=5
RECIPIENTS="user@domain.tld"
MAILSERVER="user@server.domain.tld"
ERROR=$(bc <<< "$TIMING>$LIMIT")
if [ "$ERROR" -gt "0" ]; then
    ssh $MAILSERVER "echo \"Warning! API request took $TIMING seconds! Threshold: $LIMIT\" | mail -s \"Integreat API Warning\" $RECIPIENTS"
fi

