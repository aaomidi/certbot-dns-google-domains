from typing import Callable, Optional, List
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
import zope.interface
import requests

from certbot import errors, interfaces
from certbot.plugins import dns_common


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AcmeTxtRecord:
    fqdn: str
    digest: str
    update_time: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RotateChallengesRequest:
    access_token: str
    records_to_add: List[AcmeTxtRecord]
    records_to_remove: List[AcmeTxtRecord]
    keep_expired_records: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AcmeChallengeSet:
    record: List[AcmeTxtRecord]


class GDSApi:
    ROTATE_CHALLENGES: str = "https://acmedns.googleapis.com/v1/{domain}:rotateChallenges"
    DEFAULT_TIMEOUT: int = 30  # 30 seconds timeout

    access_token: Optional[str]

    def __init__(self, access_token: str):
        self.access_token = access_token

    def rotate_challenges(self, domain: str, validation_name: str, validation_token: str) -> Optional[AcmeChallengeSet]:
        record_add = AcmeTxtRecord(validation_name + domain, validation_token)
        rotate_req = RotateChallengesRequest(
            self.access_token, [record_add], None, True)
        result = requests.post(self.ROTATE_CHALLENGES.format(
            domain=domain), json=rotate_req.to_json(), timeout=self.DEFAULT_TIMEOUT)
        if result.status_code != 200:
            return None
        return AcmeChallengeSet.from_json(result.text)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """ DNS Authenticator for Google Domains.
    Google Domains DNS Authenticator handles the fullfillment of dns-01 challenges.
    """

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.access_token = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 10) -> None:
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds)
        add('credentials', help='Google Domains credentials INI file.', default=None)

    def _validate_credentials(self, credentials: dns_common.CredentialsConfiguration) -> None:
        self.access_token = credentials.conf('access-token')
        if not self.access_token:
            raise errors.PluginError('{}: access_token was not found in the configuration for Google Domains.'.format(
                credentials.confobj.filename))

    def _setup_credentials(self):
        self._configure_credentials(
            'credentials',
            'Google Domains credentials INI file',
            None,
            self._validate_credentials
        )

    def _perform(self, domain: str, validation_name: str, validation_token: str) -> None:
        gds_api = self._get_gds_api()
        result = gds_api.rotate_challenges(
            domain, validation_name, validation_token)
        print(result)

    def _get_gds_api(self) -> GDSApi:
        return GDSApi(self.access_token)

    def _cleanup(self, domain, validation_name, validation):
      return
