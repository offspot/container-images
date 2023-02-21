WikiFundi
=========

A configured Mediawiki that works in pair with a content package (SQLite DB, images and custom MW config)

## Usage

### localhost

```sh
docker run -p 80:80 -p 7231:7231 -p 10044:10044 -v PATH_TO_PACKAGE:/var/www/data offspot/wikifundi
```

- MediaWiki is served via nginx on port `80`.
- Port `10044` exposes mathoid web service used for math expression rendering
- Port `7231` exposes restbase web service used for math expression rendering

### Proxied

In a standard deployment, WikiFundi is served over a dedicated domain name. Its base URL must be provided to MediaWiki configuration, via `URL` environ.

**WARNINGS**:

- The `Math` extension uses two web services to render math expressions on the Wiki. Those two web services must be exposed

- one, specified via `RESTBASE_URL` should be mapped to port `7321`
- one, specified via `MATHOID_URL ` should be mapped to port `10044`
- `RESTBASE_URL` is used **both from MW PHP code and client JS Code**. It must thus be resolvable from both the end-user (DNS entry) and via the docker container itself.

#### Sample commands

**Simple, single domain, wikifundi setup**

```sh
docker run \
    -p 80:80 -p 7231:7231 -p 10044:10044 \
    -e URL="http://wikifundi-fr.offspot" \
    -v PATH_TO_PACKAGE:/var/www/data offspot/wikifundi
```

- MediaWiki served from http://wikifundi-fr.offspot
- Math services served from http://wikifundi-fr.offspot:7231 and http://wikifundi-fr.offspot:10044

**Safer, multiple domains setup (can host several wikifundi images)***


```sh
docker run \
    --name wikifundi-fr \
    -e URL="http://wikifundi-fr.offspot" \
    -e RESTBASE_URL="http://restbase.wikifundi-fr.offspot/wikifundi-fr.offspot/" \
    -e MATHOID_URL="http://mathoid.wikifundi-fr.offspot/" \
    -v PATH_TO_PACKAGE:/var/www/data \
    offspot/wikifundi
```

- MediaWiki served from http://wikifundi-fr.offspot
- Math services served from http://restbase.wikifundi-fr.offspot and "http://mathoid.wikifundi-fr.offspot
- Requires additional DNS entries for the two services
- Requires a reverse-proxy to forward math services request to respective ports
- Note that the restbase URL includes the service domain name and the Wiki one

Here are accompanying Caddyfile and Docker Compose of a working configuration

```
{
    auto_https disable_redirects
    local_certs
    skip_install_trust
}

wikifundi-fr.offspot:80, wikifundi-fr.offspot:443 {
    tls internal
    reverse_proxy wikifundi-fr:80
}

restbase.wikifundi-fr.offspot:80 {
    reverse_proxy wikifundi-fr:7231
}

mathoid.wikifundi-fr.offspot:80 {
    reverse_proxy wikifundi-fr:10044
}
```

```yaml
---
version: '3'
services:
  reverse:
    container_name: reverse
    image: caddy:2.6.1-alpine
    ports:
    - "80:80"
    volumes:
    - ./Caddyfile:/etc/caddy/Caddyfile
  wikifundi_fr:
    image: offspot/wikifundi
    container_name: wikifundi-fr
    links:
    - reverse:restbase.wikifundi-fr.offspot
    environment:
    - URL=http://wikifundi-fr.offspot
    - RESTBASE_URL=http://restbase.wikifundi-fr.offspot/wikifundi-fr.offspot/
    - MATHOID_URL=http://mathoid.wikifundi-fr.offspot/
    volumes:
    - ./wikifundi_fr:/var/www/data
```



## Content Package specification

This image requires a specific folder tree mounted into `/var/www/data`. This *Content Package* is an export of an existing MediaWiki installation: the database (in SQLite format), the images folder and some content-specific MediaWiki configurations.

The following are mandatory:

- `images` folder tree (or empty folder)
- `mw_wikifundi.sqlite`: SQLite MediaWiki database
- `LocalSettings.custom.php`: a PHP file containing content-package specific MediaWiki configurations such as `$wgSitename`, `$wgLanguageCode`, etc.

_Important_: WikiFundi **is not a generic MediaWiki image**.

### Minimal `LocalSettings.custom.php`

```php
<?php ?>
```

### Sample `LocalSettings.custom.php`

```php
<?php

$wgSitename         = "WikiFundi";
$wgNamespacesToBeSearchedDefault = [
	NS_MAIN => true,
	NS_PROJECT => true,
	NS_CATEGORY => true,
	4 => true,
	NS_HELP => true,
	NS_USER => true,
];

// Site language
$wgLanguageCode = "fr";
$wgULSLanguageDetection = false; // don't detect user agent language
$wgUploadWizardConfig['uwLanguages'] = [ 'fr' => 'French' ];
$wgUploadWizardConfig['tutorial']['skip'] = true;

// Set FR Wikipédia namespace
$wgExtraNamespaces[NS_FOO] = "Wikipédia";
$wgExtraNamespaces[NS_FOO_TALK] = "Wikipédia_talk"; // Note underscores in the namespace name.

?>
```