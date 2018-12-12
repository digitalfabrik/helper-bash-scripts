<?php
$info = $_SERVER['HTTP_USER_AGENT'];

$android        = strpos($info, 'Android') ? true : false;
if (strpos($info, 'Android') || strpos($info, 'android')) {
        $android = true;
} else {
        $android = false;
}

if (strpos($info, 'Windows')) {
        $windows = true;
} else {
        $windows = false;
}

if (strpos($info, 'iPhone') || strpos($info, 'iOS') || strpos($info, 'iPad')) {
        $iphone = true;
} else {
        $iphone = false;
}

if($_GET['debug']) {
        var_dump($android);
        var_dump($windows);
        var_dump($iphone);
        echo "<br>$info<br>";
} else {

if($android)
        header('Location: https://play.google.com/store/apps/details?id=tuerantuer.app.integreat');
elseif($windows)
        header('Location: https://web.integreat-app.de');

elseif($iphone)
        header('Location: https://itunes.apple.com/de/app/integreat/id1072353915?mt=8&ign-mpt=uo%3D2');

else
        header('Location: https://web.integreat-app.de');

}
?>

