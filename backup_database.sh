#!/bin/bash
CURRENT_DATE=$(date +%Y%m%d-%H%M)
mkdir /tmp/ig-backup
mysqldump -u root ig_cms > /tmp/database.sql
bzip2 /tmp/database.sql
openssl rand -base64 32 > /root/key.bin
openssl enc -aes-256-cbc -salt -in /tmp/database.sql.bz2 -out /tmp/ig-backup/database-$CURRENT_DATE.sql.bz2.enc -pass file:/root/key.bin
openssl rsautl -encrypt -inkey /root/backup_pubkey.pem -pubin -in /root/key.bin -out /tmp/ig-backup/key-$CURRENT_DATE.bin.enc
rm /root/key.bin
cd /tmp/ig-backup
find ./ -mtime +1 -type f -delete

