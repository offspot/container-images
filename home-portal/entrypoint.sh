#!/bin/sh

# generate SSL certificate for the IP
CSR_PATH=/etc/ssl/captive.csr
CERT_PATH=/etc/ssl/captive.crt
CERT_KEY_PATH=/etc/ssl/captive.key

if [ ! -f $CERT_PATH ]; then
	echo "Generating self-signed SSL certificate for ${HOTSPOT_IP}"
	cat << EOF > $CSR_PATH
[req]
default_bits           = 2048
default_keyfile        = server-key.pem
prompt                 = no
default_md             = sha384
req_extensions         = req_ext
x509_extensions        = x509_ext
distinguished_name     = req_distinguished_name
string_mask            = utf8only

[req_distinguished_name]
countryName            = CH
stateOrProvinceName    = Vaud
organizationName       = Kiwix
organizationalUnitName = Kiwix Hotspot
commonName             = kiwix.hotspot
emailAddress           = hotspot@kiwix.org

[req_ext]
subjectAltName         = @alt_names

[x509_ext]
basicConstraints       = CA:FALSE

[alt_names]
IP.1                   = ${HOTSPOT_IP}
DNS.1                  = ${HOTSPOT_FQDN}
DNS.2                  = *.${HOTSPOT_FQDN}
EOF
	openssl req -config $CSR_PATH -new -x509 -newkey rsa:2048 -nodes -keyout $CERT_KEY_PATH -days 3650 -out $CERT_PATH -batch
fi

caddy run --config /etc/caddy/Caddyfile &

exec "$@"
