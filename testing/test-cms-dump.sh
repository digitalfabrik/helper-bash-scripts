#!/bin/bash
mysqldump -u root ig_cms > /root/ig_cms.sql
mysql ig_export_db < /root/ig_cms.sql
rm /root/ig_cms.sql
mysql ig_export_db -e "UPDATE wp_users SET user_email='';"
LIST=$(mysql --batch -e "SHOW TABLES" ig_export_db | grep "_options")
while IFS= read -r TABLE; do; mysql ig_export_db -e "UPDATE $TABLE SET option_value=\"\" WHERE option_name=\"wp-piwik_global-piwik_token\";"; done <<< $LIST
mysqldump -u root ig_export_db > /root/ig_export_db.sql
rsync /root/ig_export_db.sql server9.tuerantuer.org:/root
rsync -avr --progress /var/www/cms/wp-content/uploads/ sven@server9.integreat-app.de:/var/www/cms/wp-content/
