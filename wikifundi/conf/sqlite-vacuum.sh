#!/bin/sh

# periodic cleanup of SQLite DB
echo "vacuuming database"

cd ${WIKIFUNDI_DATA}
php maintenance/sqlite.php --vacuum > /dev/null
ret=$?
echo "> $ret"
