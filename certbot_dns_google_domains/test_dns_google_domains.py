import pytest
from certbot_dns_google_domains.dns_google_domains import Authenticator
from publicsuffixlist import PublicSuffixList


class TestGetZone:
    def test_with_cli_argument(self):
        # Set up
        domain = "example.com"
        from_config = None
        from_cli = "cli_zone"
        psl = PublicSuffixList()

        # Test
        result = Authenticator._get_zone(domain, from_config, from_cli, psl)
        # Verify
        assert result == "cli_zone"

    def test_with_config_setting(self):
        # Set up
        domain = "example.com"
        from_config = "config_zone"
        from_cli = None
        psl = PublicSuffixList()

        # Test
        result = Authenticator._get_zone(domain, from_config, from_cli, psl)

        # Verify
        assert result == "config_zone"

    def test_with_domain_suffix(self):
        # Set up
        domain = "subdomain.example.com"
        from_config = None
        from_cli = None
        psl = PublicSuffixList()

        # Test
        result = Authenticator._get_zone(domain, from_config, from_cli, psl)
        # Verify
        assert result == "example.com"

    def test_with_no_setting(self):
        # Set up
        domain = "example.com"
        from_config = None
        from_cli = None
        psl = PublicSuffixList()

        # Test
        result = Authenticator._get_zone(domain, from_config, from_cli, psl)

        # Verify
        assert result == "example.com"
