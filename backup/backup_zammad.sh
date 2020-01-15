#!/bin/bash
TARGET=""
CURRENT_DATE=$(date +%Y%m%d-%H%M)
tar --dereference -cf ~/zammad-$CURRENT_DATE.tar /var/backups/zammad/latest_zammad_db.psql.gz /var/backups/zammad/latest_zammad_files.tar.gz
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/zammad-$CURRENT_DATE.tar -out ~/zammad-$CURRENT_DATE.tar.enc -pass file:$HOME/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out /root/key-$CURRENT_DATE.bin.enc
rm ~/key.bin
if [ -n "$TARGET" ]; then
  scp ~/key-$CURRENT_DATE.bin.enc $TARGET
  scp ~/zammad-$CURRENT_DATE.tar.enc $TARGET
fi
rm ~/zammad-$CURRENT_DATE.tar
