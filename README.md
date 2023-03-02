# certbot-dns-google-domains

A Certbot DNS Authenticator for [Google Domains](https://domains.google/).

## Named Arguments

Option|Description
---|---|
`--authenticator dns-google-domains`|Select this authenticator plugin.
`--dns-google-domains-credentials FILE`|Path to the INI file with credentials.
`--dns-google-domains-propagation-seconds INT`|How long to wait for DNS changes to propagate. Default = 30s.
`--dns-google-domains-zone STRING`|What the registered domain on Google domains is. This is required if you are requesting a certificate for a sub-domain. Default = None.

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
  --server 'https://acme-v02.api.letsencrypt.org/directory' \
  --dns-google-domains-zone 'example.com' \
  -d 'a.example.com'
```

Notes:
- `-v '/var/lib/letsencrypt:/var/lib/letsencrypt'` is where certbot by default outputs certificates, keys, and account information.
- `-v '/etc/letsencrypt:/etc/letsencrypt'` is where certbot keeps its configuration.
- `--authenticator 'dns-google-domains'` uses the dns-google-domains authenticator.
- `--dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini'` is the path to the credentials file.
- `--dns-google-domains-zone 'example.com'` is the main domain you have registered with Google domains. This is required if you're issuing certificates for a subdomain.


### Python

You can get the `certbot-dns-google-domains` package from [PyPi](https://pypi.org/project/certbot-dns-google-domains/):

```bash
pip3 install certbot certbot-dns-google-domains

certbot certonly \
--authenticator 'dns-google-domains' \
--dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini' \
--server 'https://acme-v02.api.letsencrypt.org/directory' \
--dns-google-domains-zone 'example.com' \
-d 'a.example.com'
```
