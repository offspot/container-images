<?php

/*
Rewrite config.php and manager_auth.php to replace expected patterns based on
envrion values.
*/

// APP_URL must not be set in mixed mode as there are two distinct URLs
if (getenv("ACCESS_MODE") == "mixed"){
    $_SERVER['APP_URL'] = '';
}

foreach (array('config.php', 'manager_auth.php') as $fname) {
    $config_text = file_get_contents($fname);
    foreach(array("ADMIN_USERNAME", "ADMIN_PASSWORD", "UI_TIMEZONE", "UI_LANG", "APP_URL") as $pattern) {
        $config_text = str_replace($pattern, getenv($pattern), $config_text);
    }
    file_put_contents($fname, $config_text);
}

?>
