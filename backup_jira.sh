#!/bin/bash
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir /tmp/jira-backup ~/jira/
mysqldump -u root jiradb > ~/database.sql
rsync -a --exclude /var/atlassian/application-data/jira/plugins --exclude /var/atlassian/application-data/jira/data/git-plugin /var/atlassian/application-data/jira/* ~/jira/
tar -cf ~/backup.tar ~/database.sql ~/jira/
bzip2 ~/database.tar
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/database.tar.bz2 -out /tmp/jira-backup/database-$CURRENT_DATE.tar.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out /tmp/jira-backup/key-$CURRENT_DATE.bin.enc
chmod -R 777 /tmp/jira-backup
rm ~/key.bin
rm ~/database.sql
rm ~/database.tar.bz2
rm -rf ~/jira/
cd /tmp/jira-backup
find ./ -mtime +1 -type f -delete

