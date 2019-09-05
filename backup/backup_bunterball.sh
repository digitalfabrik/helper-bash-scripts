#!/bin/bash
TARGET=""
BACKUPDIR="/var/backup/bunterball/"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir -p $BACKUPDIR
chmod -R 700 $BACKUPDIR
find /home/bunterball/ -name db.sqlite3 -exec cp {} ~/db.sqlite3 \; -quit
bzip2 ~/db.sqlite3
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/db.sqlite3.bz2 -out $BACKUPDIR/db-$CURRENT_DATE.sqlite3.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out $BACKUPDIR/key-$CURRENT_DATE.bin.enc
rm ~/key.bin
rm ~/db.sqlite3.bz2
if [ -n "$TARGET" ]; then
  scp $BACKUPDIR/key-$CURRENT_DATE.bin.enc $TARGET
  scp $BACKUPDIR/db-$CURRENT_DATE.sqlite3.bz2.enc $TARGET
fi
find $BACKUPDIR -mtime +7 -type f -delete
