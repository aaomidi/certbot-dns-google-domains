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

import logging
from typing import Callable, Optional, List
from dataclasses import dataclass, field
import requests
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import zope.interface

from certbot import errors, interfaces
from certbot.plugins import dns_common
from publicsuffixlist import PublicSuffixList

logger = logging.getLogger(__name__)

@dataclass
class AcmeTxtRecord(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)[
        "dataclasses_json"]
    fqdn: str
    digest: str
    update_time: Optional[str] = field(default=None, metadata=config(
        exclude=lambda f: f is None))  # type: ignore


@dataclass
class RotateChallengesRequest(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)[
        "dataclasses_json"]

    access_token: str
    records_to_add: Optional[List[AcmeTxtRecord]] = field(default=None, metadata=config(
        exclude=lambda f: f is None))  # type: ignore
    records_to_remove: Optional[List[AcmeTxtRecord]] = field(default=None, metadata=config(
        exclude=lambda f: f is None))  # type: ignore
    keep_expired_records: bool = False


@dataclass
class AcmeChallengeSet(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)[
        "dataclasses_json"]
    record: Optional[List[AcmeTxtRecord]]


class GDSApi:
    ROTATE_CHALLENGES: str = "https://acmedns.googleapis.com/v1/acmeChallengeSets/{domain}:rotateChallenges"
    DEFAULT_TIMEOUT: int = 30  # 30 seconds timeout
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    def rotate_challenges(self, zone: str, rotate_req: RotateChallengesRequest) -> Optional[AcmeChallengeSet]:
        request_json = rotate_req.to_json()

        url = self.ROTATE_CHALLENGES.format(domain=zone)
        result = requests.post(
            url, data=request_json, timeout=self.DEFAULT_TIMEOUT,
            headers={"Content-Type": "application/json; charset=utf-8"})

        rotate_req.access_token = ""
        sanitized_json = rotate_req.to_json()
        logger.debug(
            f"Request to {url} returned {result.status_code} {result.text} with data {sanitized_json}")
        result.raise_for_status()

        return AcmeChallengeSet.from_json(result.text)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """ DNS Authenticator for Google Domains.
    Google Domains DNS Authenticator handles the fullfillment of dns-01 challenges.
    """

    access_token: str
    zone_from_credentials: str
    psl: PublicSuffixList = PublicSuffixList()

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 30) -> None:
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds)
        add('credentials', help='Google Domains credentials INI file.', default=None)
        add('zone', help="The zone (base domain) under Google Domains. For example, example.com if requesting for a.example.com",
            default=None, required=False)

    def _validate_credentials(self, credentials: dns_common.CredentialsConfiguration) -> None:
        self.access_token = credentials.conf('access-token')
        if not self.access_token:
            raise errors.PluginError(errors.MisconfigurationError(
                f'{credentials.confobj.filename}: access_token was not found in the configuration for Google Domains.'))
        self.zone_from_credentials = credentials.conf('zone')

    def _setup_credentials(self):
        self._configure_credentials(
            'credentials',
            'Google Domains credentials INI file',
            None,
            self._validate_credentials
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        gds_api = self._get_gds_api()
        record_add = AcmeTxtRecord(validation_name, validation)
        rotate_req = RotateChallengesRequest(
            self.access_token, [record_add], None, False)

        zone = self._get_zone(
            domain, self.zone_from_credentials, self.conf('zone'), self.psl)
        logger.info(f"Zone selected for {domain}: {zone}")
        try:
            gds_api.rotate_challenges(zone, rotate_req)
        except Exception as err:
            raise errors.PluginError(f"Unable to rotate DNS challenges: {err}")

    def _get_gds_api(self) -> GDSApi:
        return GDSApi(self.access_token)

    def _cleanup(self, domain: str, validation_name: str, validation: str):
        gds_api = self._get_gds_api()
        record_remove = AcmeTxtRecord(validation_name, validation)
        rotate_req = RotateChallengesRequest(
            self.access_token, None, [record_remove], True)

        zone = self._get_zone(
            domain, self.zone_from_credentials, self.conf('zone'), self.psl)
        try:
            gds_api.rotate_challenges(zone, rotate_req)
        except Exception as err:
            raise errors.PluginError(f"Unable to rotate DNS challenges: {err}")
        return

    @staticmethod
    def _get_zone(domain: str, from_config: Optional[str], from_cli: Optional[str], psl: PublicSuffixList) -> str:
        # First let's check if there is anything passed in as a CLI argument
        if from_cli is not None:
            return from_cli

        # If not, get the zone passed in by the credentials file
        if from_config is not None:
            return from_config

        # If not, let's try to get the zone from the domain
        return psl.privatesuffix(domain)  # type: ignore
