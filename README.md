# certbot-dns-google-domains

A Certbot DNS Authenticator for [Google Domains](https://domains.google/).

## Named Arguments

Option|Description
---|---|
`--authenticator dns-google-domains`|Select this authenticator plugin.
`--dns-google-domains-credentials FILE`|Path to the INI file with credentials.
`--dns-google-domains-propagation-seconds INT`|How long to wait for DNS changes to propagate. Default = 30s.
`--dns-google-domains-zone STRING`|What the registered domain on Google domains is. Default: Retrieved from either the credentials file, or by using the public suffix list to guess.

## Credentials

The credentials file includes the access token for Google Domains.

```.ini
dns_google_domains_access_token = abcdef
```

Optionally, you can also define the zone in this file.

```.ini
dns_google_domains_access_token = abcdef
dns_google_domains_zone = example.com
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
  --non-interactive \
  --dns-google-domains-zone 'example.com' \
  -d 'a.example.com'
```

Notes:
- `-v '/var/lib/letsencrypt:/var/lib/letsencrypt'` is where certbot by default outputs certificates, keys, and account information.
- `-v '/etc/letsencrypt:/etc/letsencrypt'` is where certbot keeps its configuration.
- `--authenticator 'dns-google-domains'` uses the dns-google-domains authenticator.
- `--dns-google-domains-credentials '/var/lib/letsencrypt/dns_google_domains_credentials.ini'` is the path to the credentials file.
- `--dns-google-domains-zone 'example.com'` is the main domain you have registered with Google domains. This is optional.
- To ensure successful execution, this command requires you to intentionally provide both the --email and --agree-tos arguments. The command does not include them by default, as it is important for users to consciously agree to the terms of service and supply their email address.

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

Note: If you have installed Certbot from a non-pip3 source, the certbot-dns-google-domains plugin might not be compatible with your existing Certbot installation. In this case, consider using pip3 to install Certbot and its plugins to ensure compatibility.

### Homebrew

```bash
brew install certbot
$(brew --prefix certbot)/libexec/bin/pip3 install certbot-dns-google-domains
```

## Notes on Zone Resolution

Google Domains does not provide an API to obtain the zone for a domain based on a subdomain. This plugin employs the following logic to determine the zone:

1. If the `--dns-google-domains-zone` argument is specified, use that.
2. If the credentials file specifies a zone, use that.
3. Utilize the [Public Suffix List](https://publicsuffix.org/) to determine the zone.

