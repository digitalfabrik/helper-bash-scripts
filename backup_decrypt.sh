#!/bin/bash
if [[ -z $1 || $1 == "--help" || $1 == "-h" ]]; then
	echo "Usage: decrypt_database.sh [PRIVKEY] [AES_KEY] [DATABASE]"
	exit
fi
openssl rsautl -decrypt -inkey $1 -in $2 -out ~/key.bin
openssl enc -d -aes-256-cbc -in $3 -out ~/database.sql.bz2 -pass file:~/key.bin 
