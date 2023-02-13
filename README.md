# certbot-dns-google-domains

## Named Arguments

Option|Description
---|---|
`--authenticator dns-google-domains`|Select this authenticator plugin.
`--dns-google-domains-credentials FILE`|Path to the INI file with credentials.
`--dns-google-domains-propagation-seconds INT`|How long to wait for DNS changes to propagate. Default = 30s.

## Credentials

The credentials file includes the access token for Google Domains.

```.ini
dns_google_domains_access_token = abcdef
```

## Usage Example

### Docker / Podman

``` bash
docker run \
  -v '/var/lib/letsencrypt:/var/lib/letsencrypt' \
  -v '/etc/letsencrypt:/etc/letsencrypt' \
  --cap-drop=all \
  ghcr.io/aaomidi/certbot-dns-google-domains:latest \
  certbot certonly \
  --authenticator 'dns-google-domains' \
  --dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini' \
  --no-eff --non-interactive --server 'https://acme-staging-v02.api.letsencrypt.org/directory' \
  --agree-tos --email 'email@example.com' -d 'example.com'
```

Notes:
- `-v '/var/lib/letsencrypt:/var/lib/letsencrypt'` is where certbot by default outputs certificates, keys, and account information.
- `-v '/etc/letsencrypt:/etc/letsencrypt'` is where certbot keeps its configuration.
- `--authenticator 'dns-google-domains'` uses the dns-google-domains authenticator.
- `--dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini'` is the path to the credentials file.
