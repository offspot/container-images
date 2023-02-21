#!/bin/bash

set -e

echo "Preparing data for statup…"
DATABASE_FILE=${WIKIFUNDI_DATA}/${DATABASE_NAME}.sqlite

echo "> Ensuring proper folder structure and permissions"
mkdir -m 755 -p ${CACHE_DIR} && chown www-data:www-data -R ${CACHE_DIR}
mkdir -p ${WIKIFUNDI_DATA}/images
if [ -z "$NOCHOWN" ] ; then
  chown -R www-data:www-data ${WIKIFUNDI_DATA}
fi

if [ ! -z "$MWDEBUG" ] ; then
    echo "> Enable MediaWiki debugging"
    cat <<EOF >> ${MEDIAWIKI_ROOT}/LocalSettings.php

// debug
error_reporting( -1 );
ini_set( 'display_errors', 1 );
\$wgShowExceptionDetails=true;
\$wgShowDBErrorBacktrace = true;
\$wgDebugToolbar=true;
\$wgShowDebug=true;
\$wgDevelopmentWarnings=true;

EOF
fi

if [ -z "$URL" ] ; then
  echo "### WARNING: no URL environ set. Defaulting to http://localhost"
fi

# RESTBASE_URL to contain passes url if set
# otherwise default to {scheme}://{domain}:7231/{domain}/ if $URL is set
# otherwise similar format for localhost
RESTBASE_URL=$(cat <<EOF | python3
import os
import sys
import urllib.parse
if os.getenv('RESTBASE_URL'):
    print(os.getenv('RESTBASE_URL'))
    sys.exit(0)
if os.getenv('URL') and os.getenv('URL') != "http://localhost":
    uri = urllib.parse.urlparse(os.getenv('URL'))
    print(f'{uri.scheme}://{uri.hostname}:7231/{uri.hostname}/')
else:
    print('http://localhost:7231/localhost/')
EOF
)

RESTBASE_HOSTNAME=$(cat <<EOF | python3
import os
import urllib.parse
uri = urllib.parse.urlparse(os.getenv('RESTBASE_URL'))
print(uri.hostname)
EOF
)

# MATHOID_URL to contain passed url if set
# otherwise default to {scheme}://{domain}:10044/ if $URL is set
# otherwise similar format for localhost
MATHOID_URL=$(cat <<EOF | python3
import os
import sys
import urllib.parse
if os.getenv('MATHOID_URL'):
    print(os.getenv('MATHOID_URL'))
    sys.exit(0)
if os.getenv('URL') and os.getenv('URL') != "http://localhost":
    uri = urllib.parse.urlparse(os.getenv('URL'))
    print(f'{uri.scheme}://{uri.hostname}:10044/')
else:
    print('http://localhost:10044/')
EOF
)

cat <<EOF >> ${MEDIAWIKI_ROOT}/LocalSettings.php

// URLs
\$wgServer = "${URL}";
\$wgCanonicalServer = "${URL}";
\$wgMathFullRestbaseURL = "${RESTBASE_URL}";
\$wgMathMathMLUrl = "${MATHOID_URL}";

EOF

if [ ! -z "$DEBUG" ] ; then
  echo "##############################################"
  cat ${MEDIAWIKI_ROOT}/LocalSettings.php
  echo "##############################################"
fi

# echo "> Adding RESTBASE_HOSTNAME (${RESTBASE_HOSTNAME}) to /etc/hosts"
# echo "127.0.0.1  ${RESTBASE_HOSTNAME}" >> /etc/hosts

echo "> Making sure DB is writable"
chmod 644 ${DATABASE_FILE} && chown www-data:www-data ${DATABASE_FILE}

# Fix latence problem
echo "> Removing locks"
rm -rf ${WIKIFUNDI_DATA}/locks

service memcached start

service mathoid start

service restbase start

echo "starting php7.4-fpm…"
service php7.4-fpm start

service cron start

echo "> Setting Admin user password"
php maintenance/createAndPromote.php --bureaucrat --sysop --force Admin ${MEDIAWIKI_ADMIN_PASSWORD}

echo "Now switching to CMD ($@)"
exec "$@"
