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
    update_time: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RotateChallengesRequest:
    access_token: str
    records_to_add: Optional[List[AcmeTxtRecord]] = None
    records_to_remove: Optional[List[AcmeTxtRecord]] = None
    keep_expired_records: bool = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AcmeChallengeSet:
    record: List[AcmeTxtRecord]


class GDSApi:
    TOKEN: str = "https://www.googleapis.com/oauth2/v4/token"
    ROTATE_CHALLENGES: str = "https://acmedns.googleapis.com/v1/acmeChallengeSets/{domain}:rotateChallenges"
    DEFAULT_TIMEOUT: int = 30  # 30 seconds timeout
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_access_token(self):


    def rotate_challenges(self, domain: str, validation_name: str, validation_token: str) -> Optional[AcmeChallengeSet]:
        record_add = AcmeTxtRecord(validation_name, validation_token)
        rotate_req = RotateChallengesRequest(
            self.access_token, [record_add], None, True)
        request_json = rotate_req.to_json()
        print(request_json)

        url = self.ROTATE_CHALLENGES.format(
            domain=domain)
        result = requests.post(
            url, data=request_json, timeout=self.DEFAULT_TIMEOUT,
            headers={"Content-Type": "application/json"})
        print(result.text)
        if result.status_code != 200:
            return None

        return AcmeChallengeSet.from_json(result.text)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """ DNS Authenticator for Google Domains.
    Google Domains DNS Authenticator handles the fullfillment of dns-01 challenges.
    """

    access_token: str

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 30) -> None:
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
