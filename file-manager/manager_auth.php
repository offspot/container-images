<?php

// Auth with login/password
// set true/false to enable/disable it
// Is independent from IP white- and blacklisting
$use_auth = true;

// Global readonly, including when auth is not being used
$global_readonly = false;

// Login user name and password
// Users: array('Username' => 'Password', 'Username2' => 'Password2', ...)
// Generate secure password hash - https://tinyfilemanager.github.io/docs/pwd.html
$auth_users = array(
    'ADMIN_USERNAME' => password_hash('ADMIN_PASSWORD', PASSWORD_DEFAULT),
);

?>
