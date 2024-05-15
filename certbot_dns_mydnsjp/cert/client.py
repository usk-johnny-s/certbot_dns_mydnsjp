from certbot import errors
from certbot.plugins import dns_common

from certbot_dns_mydnsjp.mydnsjp.client import MyDNSJPClient

DEFAULT_PROPAGATION_SECONDS = 30
ACME_CHALLENGE_TXT_PREFIX = "_acme-challenge"

class Authenticator(dns_common.DNSAuthenticator):
    """
    Authenticator class to handle dns-01 challenge with MyDNS.JP.
    """

    description = "Obtain certificates using a DNS TXT record with MyDNS.JP"
    _mydnsjp_client = None
    _prev_txt_contents = None

    def __init__(self, *args, **kwargs) -> None:
        super(Authenticator, self).__init__(*args, **kwargs)
        self._mydnsjp_client = None
        self._prev_txt_contents = None

    @classmethod
    def add_parser_arguments(cls, add: callable) -> None:
        """
        Add required or optional argument for the cli of certbot.

        :param add: method handling the argument adding to the cli
        """

        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=DEFAULT_PROPAGATION_SECONDS)
        add("credentials", help="MyDNS.JP credentials INI file.")
        add("no-txt-restore",
            default=False,
            action="store_true",
            help="Do not restore the original TXT record")

    def more_info(self) -> str:
        """
        Get more information about this plugin.
        This method is used by certbot to show more info about this plugin.

        :return: string with more information about this plugin
        """
        return "This plugin configures a DNS TXT record to respond to a DNS-01 challenge using the MyDNS.JP web interface."

    def _setup_credentials(self) -> None:
        self._configure_file('credentials',
                             'MyDNS.JP credentials INI file')
        dns_common.validate_file_permissions(self.conf('credentials'))
        self.credentials = self._configure_credentials(
            "credentials",
            "MyDNS.JP credentials INI file",
            {
                "credential": "INI file contains that\n[dns_mydnsjp_credential]\n[[MyDnsJpDomain1]]\n'id'='MyDnsJpId1'\n'pwd'='MyDnsJpPwd1'\n[[MyDnsJpDomain2]]\n'id'='MyDnsJpId2'\n'pwd'='MyDnsJpPwd2'\n...}",
            },
        )
        # create MyDNSJPClient with validate credential format
        try:
            credential = self.credentials.conf("credential")
            self._mydnsjp_client = MyDNSJPClient(credential)
        except Exception as e:
            raise errors.PluginError(e)

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        """
        Add the TXT record of the provided domain using MyDNS.JP.

        :param domain: domain name set at MyDNS.JP
        :param validation_name: value to validate the dns challenge
        :param validation: the value for the TXT record
        :raise PluginError: if the TXT record can not be set of something goes wrong
        """

        challenge_domain = ACME_CHALLENGE_TXT_PREFIX + "." + domain
        try:
            # get the MyDNS.JP credential
            credential = self._get_mydnsjp_client().get_mydnsjp_credential(domain)
            # set TXT value for acme_challenge
            self._prev_txt_contents = self._get_mydnsjp_client().set_txt_record(credential, challenge_domain, validation)
        except Exception as e:
            raise errors.PluginError(e)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        """
        Clear the dns validation from the TXT record of the provided domain using MyDNS.JP.
        Restore the previous TXT value if the TXT value was not empty before the DNS challenge.

        :param domain: domain name set at MyDNS.JP
        :param validation_name: value to validate the dns challenge
        :param validation: the value for the TXT record
        :raise PluginError: if the TXT record can not be cleared of something goes wrong
        """

        challenge_domain = ACME_CHALLENGE_TXT_PREFIX + "." + domain
        if self.conf("no-txt-restore"):
            self._prev_txt_contents = None
        try:
            # get the MyDNS.JP credential
            credential = self._get_mydnsjp_client().get_mydnsjp_credential(domain)
            # delete or restore TXT value for acme_challenge
            self._get_mydnsjp_client().clear_txt_record(credential, challenge_domain, validation, self._prev_txt_contents)
        except Exception as e:
            raise errors.PluginError(e)

    def _get_mydnsjp_client(self) -> MyDNSJPClient:
        """
        Get MyDNSJPClient.

        :return: MyDNSJPClient object
        :raise Exception: if self._mydnsjp_client is None
        """
        if self._mydnsjp_client is None:
            raise Exception(f"Not initialized _mydnsjp_client.")
        return self._mydnsjp_client
