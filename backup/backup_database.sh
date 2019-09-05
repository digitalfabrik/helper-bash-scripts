#!/bin/bash
TARGET=""
BACKUPDIR="/tmp/ig-backup"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir $BACKUPDIR
mysqldump -u root ig_cms > ~/database.sql
bzip2 ~/database.sql
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/database.sql.bz2 -out $BACKUPDIR/database-$CURRENT_DATE.sql.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out $BACKUPDIR/key-$CURRENT_DATE.bin.enc
chmod -R 700 /tmp/ig-backup
rm ~/key.bin
rm ~/database.sql.bz2
if [ -n "$TARGET" ]; then
  scp $BACKUPDIR/key-$CURRENT_DATE.bin.enc $TARGET
  scp $BACKUPDIR/database-$CURRENT_DATE.sql.bz2.enc $TARGET
fi
find $BACKUPDIR -mtime +7 -type f -delete
