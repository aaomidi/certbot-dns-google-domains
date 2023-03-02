from typing import Callable, Optional, List
from dataclasses import dataclass, field
import requests
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import zope.interface

from certbot import errors, interfaces
from certbot.plugins import dns_common


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
    record: List[AcmeTxtRecord]


class GDSApi:
    ROTATE_CHALLENGES: str = "https://acmedns.googleapis.com/v1/acmeChallengeSets/{domain}:rotateChallenges"
    DEFAULT_TIMEOUT: int = 30  # 30 seconds timeout
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    def rotate_challenges(self, domain: str, rotate_req: RotateChallengesRequest) -> Optional[AcmeChallengeSet]:
        request_json = rotate_req.to_json()

        url = self.ROTATE_CHALLENGES.format(domain=domain)
        result = requests.post(
            url, data=request_json, timeout=self.DEFAULT_TIMEOUT,
            headers={"Content-Type": "application/json; charset=utf-8"})
        result.raise_for_status()

        return AcmeChallengeSet.from_json(result.text)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """ DNS Authenticator for Google Domains.
    Google Domains DNS Authenticator handles the fullfillment of dns-01 challenges.
    """

    access_token: str

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 30) -> None:
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds)
        add('credentials', help='Google Domains credentials INI file.', default=None)
        add('zone', help="The zone (base domain) under Google Domains. For example, example.com if requesting for a.example.com", default=None, required=False)

    def _validate_credentials(self, credentials: dns_common.CredentialsConfiguration) -> None:
        self.access_token = credentials.conf('access-token')
        if not self.access_token:
            raise errors.PluginError(errors.MisconfigurationError(f'{credentials.confobj.filename}: access_token was not found in the configuration for Google Domains.'))

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
            self.access_token, [record_add], None, True)
        zone = self.conf('zone')
        if zone is None:
            zone = domain
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
        try:
            gds_api.rotate_challenges(domain, rotate_req)
        except Exception as err:
            raise errors.PluginError(f"Unable to rotate DNS challenges: {err}")
        return
