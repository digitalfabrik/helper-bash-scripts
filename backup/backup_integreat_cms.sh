#!/bin/bash
TARGET=""
BACKUPDIR="/var/backup/cms-database"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
OLD_UMASK=$(umask)
umask 177
mkdir -p $BACKUPDIR
mysqldump -u root ig_cms > ~/database.sql
tar -cf - /var/www/cms/wp-content/uploads ~/database.sql | gzip -9 > ~/integreat-cms.tar.gz
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/integreat-cms.tar.gz -out $BACKUPDIR/integreat-cms-$CURRENT_DATE.tar.gz.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out $BACKUPDIR/key-$CURRENT_DATE.bin.enc
rm ~/key.bin
rm ~/integreat-cms.tar.gz
rm ~/database.sql
if [ -n "$TARGET" ]; then
  scp $BACKUPDIR/key-$CURRENT_DATE.bin.enc $TARGET
  scp $BACKUPDIR/integreat-cms-$CURRENT_DATE.tar.gz.enc $TARGET
fi
find $BACKUPDIR -mtime +7 -type f -delete
umask $OLD_UMASK
