#!/bin/bash
TARGET=""
BACKUPDIR="/var/backup/wiki"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir -p $BACKUPDIR
chmod -R 700 $BACKUPDIR
tar -cf ~/backup.tar /var/www/wiki.integreat-app.de/ /var/www/wiki.tuerantuer.org/
bzip2 ~/backup.tar
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/backup.tar.bz2 -out $BACKUPDIR/backup-$CURRENT_DATE.tar.bz2.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out $BACKUPDIR/key-$CURRENT_DATE.bin.enc
rm ~/key.bin
rm ~/backup.tar.bz2
if [ -n "$TARGET" ]; then
  scp $BACKUPDIR/key-$CURRENT_DATE.bin.enc $TARGET
  scp $BACKUPDIR/backup-$CURRENT_DATE.tar.bz2.enc $TARGET
fi
find $BACKUPDIR -mtime +7 -type f -delete
