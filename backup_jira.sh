#!/bin/bash
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir /tmp/jira-backup /tmp/jira-backup/jira/
mysqldump -u root jiradb > ~/database.sql
rsync -a --exclude /var/atlassian/application-data/jira/plugins --exclude /var/atlassian/application-data/jira/data/git-plugin /var/atlassian/application-data/jira/* /tmp/jira-backup/jira/
bzip2 ~/database.sql
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/database.sql.bz2 -out /tmp/jira-backup/database-$CURRENT_DATE.sql.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out /tmp/jira-backup/key-$CURRENT_DATE.bin.enc
chmod -R 777 /tmp/jira-backup
rm ~/key.bin
rm ~/database.sql.bz2
cd /tmp/jira-backup
find ./ -mtime +1 -type f -delete

