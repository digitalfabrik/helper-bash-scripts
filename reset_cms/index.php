<?php
$config = parse_ini_file("config.ini");

if($_GET['reset_token'] == $config['reset_token']) {
	file_put_contents('/var/www/reset_cms', date(DateTime::ISO8601));
	file_put_contents('/var/www/webhooks/reset_done', '0');
}
?>
