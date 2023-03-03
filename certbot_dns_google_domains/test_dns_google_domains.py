# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
