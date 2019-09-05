#!/bin/bash
TARGET=""
BACKUPDIR="/var/jira-backup"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir $BACKUPDIR ~/jira/
mysqldump -u root jiradb > ~/database.sql
rsync -a --exclude /var/atlassian/application-data/jira/plugins --exclude /var/atlassian/application-data/jira/data/git-plugin /var/atlassian/application-data/jira/* ~/jira/
tar -cf ~/backup.tar ~/database.sql ~/jira/
bzip2 ~/backup.tar
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/backup.tar.bz2 -out $BACKUPDIR/backup-$CURRENT_DATE.tar.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out $BACKUPDIR/key-$CURRENT_DATE.bin.enc
chmod -R 700 $BACKUPDIR
rm ~/key.bin
rm ~/database.sql
rm ~/backup.tar.bz2
rm -rf ~/jira/
if [ -n "$TARGET" ]; then
  scp $BACKUPDIR/key-$CURRENT_DATE.bin.enc $TARGET
  scp $BACKUPDIR/backup-$CURRENT_DATE.tar.bz2.enc $TARGET
fi
find $BACKUPDIR/ -mtime +7 -type f -delete

