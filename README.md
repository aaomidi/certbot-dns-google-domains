# certbot-dns-google-domains

## Named Arguments

Option|Description
---|---|
`--authenticator dns-google-domains`|Select this authenticator plugin.
`--dns-google-domains-credentials FILE`|Path to the INI file with credentials.
`--dns-google-domains-propagation-seconds INT`|How long to wait for DNS changes to propagate. Default = 30s.

## Credentials

```.ini
dns_google_domains_access_token = abcdef
```

## Usage Example

### Docker

``` bash
docker run -v '/var/lib/letsencrypt:/var/lib/letsencrypt' -v '/etc/letsencrypt:/etc/letsencrypt' --cap-drop=all {ghcr} certonly --authenticator 'dns-google-domains' --dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini' --no-eff --non-interactive --server 'https://acme-staging-v02.api.letsencrypt.org/directory' --agree-tos --email 'email@example.com' -d 'example.com'
```

