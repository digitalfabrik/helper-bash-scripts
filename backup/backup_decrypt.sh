#!/bin/bash
if [[ -z $1 || $1 == "--help" || $1 == "-h" ]]; then
	echo "Usage: decrypt_database.sh [PRIVKEY] [AES_KEY] [DATABASE]"
	echo "In some cases you might have to add the '-md MD5' parameter to the decryption command of the database SQL file."
	exit
fi
openssl rsautl -decrypt -inkey $1 -in $2 -out ~/key.bin
# For compatibility between versions 1.0.2 and 1.1. specify MD5 as the digest
OUTNAME=$(echo $3 | sed 's/.enc//')
openssl enc -d -aes-256-cbc -in $3 -out ~/$OUTNAME -pass file:$HOME/key.bin
