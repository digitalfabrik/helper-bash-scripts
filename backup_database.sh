#!/bin/bash
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir /tmp/ig-backup
mysqldump -u root ig_cms > ~/database.sql
bzip2 ~/database.sql
openssl rand -base64 32 > ~/key.bin
openssl enc -aes-256-cbc -salt -in ~/database.sql.bz2 -out /tmp/ig-backup/database-$CURRENT_DATE.sql.bz2.enc -pass file:~/key.bin
openssl rsautl -encrypt -inkey ~/backup_pubkey.pem -pubin -in ~/key.bin -out /tmp/ig-backup/key-$CURRENT_DATE.bin.enc
rm ~/key.bin
cd /tmp/ig-backup
find ./ -mtime +1 -type f -delete

