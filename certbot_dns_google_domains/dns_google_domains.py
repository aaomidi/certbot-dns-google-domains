import logging
from typing import Callable, Type
from typing_extensions import Self
import zope.interface

from certbot import errors, interfaces
from certbot.plugins import dns_common, dns_common_lexicon


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """ DNS Authenticator for Google Domains.
    Google Domains DNS Authenticator handles the fullfillment of dns-01 challenges.
    """

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.auth = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 10) -> None:
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds)
        add('some token', help='Some token', default=None)

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
