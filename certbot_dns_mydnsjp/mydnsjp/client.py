import logging
import re
import requests
import urllib

# prevent urllib3 to log request with credential
logging.getLogger("urllib3").setLevel(logging.WARNING)

MYDNSJP_LOGIN_URL = "https://www.mydns.jp/members/"
regexp_name_of_mydnsjp_dnsinfo = re.compile("^DNSINFO\\[([^\\]]+)\\]\\[([^\\]]+)\\]",re.S|re.I)
NAME_OF_MYDNSJP_DOMAINNAME = "DNSINFO[domainname]"
KEYS_OF_MYDNSJP_MX = ["mx","prio"]
KEYS_OF_MYDNSJP_RECORD = ["hostname","type","content","delegateid"]
EXCEPT_NAMES_OF_MYDNSJP_CONFIRM = ["BACK"]

ACME_CHALLENGE_TXT_PREFIX = "_acme-challenge"

regexp_form = re.compile("<form([^>]*)>(.*?)</form[^>]*>",re.S|re.I)
regexp_select = re.compile("<select([^>]*)>(.*?)</select[^>]*>",re.S|re.I)
regexp_option = re.compile("<option([^>]*)>([^<]*)",re.S|re.I)
regexp_input = re.compile("<input([^>]*)>",re.S|re.I)
regexp_method = re.compile("\\smethod\\s*=\\s*['\"]([^'\"]+)['\"]",re.S|re.I)
regexp_action = re.compile("\\saction\\s*=\\s*['\"]([^'\"]+)['\"]",re.S|re.I)
regexp_type = re.compile("\\stype\\s*=\\s*['\"]([^'\"]+)['\"]",re.S|re.I)
regexp_name = re.compile("\\sname\\s*=\\s*['\"]([^'\"]+)['\"]",re.S|re.I)
regexp_value = re.compile("\\svalue\\s*=\\s*['\"]([^'\"]*)['\"]",re.S|re.I)
regexp_selected = re.compile("selected",re.S|re.I)

class NotValidMyDnsJpCredentialError(Exception):
    """
    Exception if the credential is not a valid format for dns_mydnsjp.
    """

    def __init__(self):
        super().__init__("The credential is not a valid format for dns_mydnsjp.")

class UpdateMyDnsJpError(Exception):
    """
    Exception if error occured at update domain info of MyDNS.JP.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MyDNSJPClient:
    """
    Client for clearing, setting the TXT record using MyDNS.JP.
    """

    def __init__(self, credential: dict) -> None:
        """
        Creates a new MyDnsJpClient object.

        :param credential: the MyDNS.JP credential used for MyDNS.JP web interface

        :raise NotValidMyDnsJpCredentialError: if the credential is not a valid format for dns_mydnsjp
        """
        if credential is None or len(credential) == 0:
            raise NotValidMyDnsJpCredentialError()
        for cred_key, cred_val in credential.items():
            if len(cred_key) == 0 or 'id' not in cred_val or 'pwd' not in cred_val:
                raise NotValidMyDnsJpCredentialError()
            if len(cred_val['id']) == 0 or len(cred_val['pwd']) == 0:
                raise NotValidMyDnsJpCredentialError()
        self._credential = credential

    def get_mydnsjp_credential(self, domain) -> dict:
        result = None
        result_key = None
        for cred_key, cred_val in self._credential.items():
            if not domain.endswith(cred_key):
                continue
            if result_key is None or len(cred_key) > len(result_key):
                result = cred_val
                result_key = cred_key
        if result is None:
            raise UpdateMyDnsJpError(f"Not found mydnsjp_credential for domain '{domain}'")
        return result

    def set_txt_record(self, credential: dict, domain: str, content: str) -> str:
        """
        Set a TXT record value for a specific domain using MyDNS.JP.

        :param credential: credential used for MyDNS.JP web interface
        :param domain: acme_challenge fully qualified domain name, provided MyDNS.JP credential must have authority of this domain.
        :param content: the string value to set as TXT record

        :return: string value of previous TXT record or None

        :raise UpdateMyDnsJpError: if unexpected sequence occured
        """
        s = requests.Session()
        request_url = MYDNSJP_LOGIN_URL
        request_method = "GET"
        r = s.request(method=request_method, url=request_url)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (LOGIN)")
        login_form_element = self._get_form_element(r.text, "/members/")
        if login_form_element is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (LoginForm missing)")
        login_form_element["masterid"]["value"] = credential["id"]
        login_form_element["masterpwd"]["value"] = credential["pwd"]
        login_form_data = self._get_form_data(login_form_element, None)
        request_url = urllib.parse.urljoin(request_url, login_form_element[""]["action"])
        request_method = login_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=login_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Get DomainInfo)")
        domain_info_form_element = self._get_form_element(r.text, "/members/#domaininfo")
        if domain_info_form_element is None:
            raise UpdateMyDnsJpError("MyDNS.JP login failed. (DomainInfoForm missing)")
        domainname = self._get_domaininame_element(domain_info_form_element)
        if domainname is None:
            raise UpdateMyDnsJpError("No configured domainname at MyDNS.JP. (domainname is None)")
        domain_suffix = "." + domainname["value"]
        if not domain.endswith(domain_suffix):
            raise UpdateMyDnsJpError("Domain suffix mismatch. (DomainInfo domainname between credential domain)")
        hostname = domain[:-len(domain_suffix)]
        record_element = self._get_record_element(domain_info_form_element)
        hostname_elements = self._find_record_element(record_element, hostname, "TXT", None)
        if hostname_elements is None:
            hostname_elements = self._find_record_element(record_element, "", "A", "")
        if hostname_elements is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (hostname_elements missing)")
        hostname_element = hostname_elements[list(hostname_elements.keys())[0]]
        prev_content = hostname_element["content"]["value"]
        if prev_content == "":
            prev_content = None
        hostname_element["hostname"]["value"] = hostname
        hostname_element["type"]["value"] = "TXT"
        hostname_element["content"]["value"] = content
        domain_info_form_data = self._get_form_data(domain_info_form_element, None)
        request_url = urllib.parse.urljoin(request_url, domain_info_form_element[""]["action"])
        request_method = domain_info_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=domain_info_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Send DomainInfo)")
        confirm_domain_info_form_element = self._get_form_element(r.text, "/members/#domaininfo")
        if confirm_domain_info_form_element is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (ConfirmForm missing)")
        confirm_domain_info_form_data = self._get_form_data(confirm_domain_info_form_element, EXCEPT_NAMES_OF_MYDNSJP_CONFIRM)
        request_url = urllib.parse.urljoin(request_url, confirm_domain_info_form_element[""]["action"])
        request_method = confirm_domain_info_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=confirm_domain_info_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Confirm DomainInfo)")
        return prev_content

    def clear_txt_record(self, credential: dict, domain: str, content: str, prev_content: str) -> None:
        """
        Clear the TXT record for a specific MyDNS.JP domain.

        :param credential: the MyDNS.JP credential used for MyDNS.JP web interface
        :param domain: acme_challenge full domain, provided MyDNS.JP credential must have authority of this domain.
        :param content: the string value to set as TXT record
        :param prev_content: string value of restoring TXT record or None (for remove)

        :raise UpdateMyDnsJpError: if unexpected sequence occured
        """
        s = requests.Session()
        request_url = MYDNSJP_LOGIN_URL
        request_method = "GET"
        r = s.request(method=request_method, url=request_url)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (LOGIN)")
        login_form_element = self._get_form_element(r.text, "/members/")
        if login_form_element is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (LoginForm missing)")
        login_form_element["masterid"]["value"] = credential["id"]
        login_form_element["masterpwd"]["value"] = credential["pwd"]
        login_form_data = self._get_form_data(login_form_element, None)
        request_url = urllib.parse.urljoin(request_url, login_form_element[""]["action"])
        request_method = login_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=login_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Get DomainInfo)")
        domain_info_form_element = self._get_form_element(r.text, "/members/#domaininfo")
        if domain_info_form_element is None:
            raise UpdateMyDnsJpError("MyDNS.JP login failed. (DomainInfoForm missing)")
        domainname = self._get_domaininame_element(domain_info_form_element)
        if domainname is None:
            raise UpdateMyDnsJpError("No configured domainname at MyDNS.JP. (domainname is None)")
        domain_suffix = "." + domainname["value"]
        if not domain.endswith(domain_suffix):
            raise UpdateMyDnsJpError("Domain suffix mismatch. (DomainInfo domainname between credential domain)")
        hostname = domain[:-len(domain_suffix)]
        record_element = self._get_record_element(domain_info_form_element)
        hostname_elements = self._find_record_element(record_element, hostname, "TXT", content)
        if hostname_elements is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (hostname_elements missing)")
        hostname_element = hostname_elements[list(hostname_elements.keys())[0]]
        if prev_content is not None:
            hostname_element["hostname"]["value"] = hostname
            hostname_element["type"]["value"] = "TXT"
            hostname_element["content"]["value"] = prev_content
        else :
            hostname_element["hostname"]["value"] = ""
            hostname_element["type"]["value"] = "A"
            hostname_element["content"]["value"] = ""
        domain_info_form_data = self._get_form_data(domain_info_form_element, None)
        request_url = urllib.parse.urljoin(request_url, domain_info_form_element[""]["action"])
        request_method = domain_info_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=domain_info_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Send DomainInfo)")
        confirm_domain_info_form_element = self._get_form_element(r.text, "/members/#domaininfo")
        if confirm_domain_info_form_element is None:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (ConfirmForm missing)")
        confirm_domain_info_form_data = self._get_form_data(confirm_domain_info_form_element, EXCEPT_NAMES_OF_MYDNSJP_CONFIRM)
        request_url = urllib.parse.urljoin(request_url, confirm_domain_info_form_element[""]["action"])
        request_method = confirm_domain_info_form_element[""]["method"].upper()
        r = s.request(method=request_method, url=request_url, data=confirm_domain_info_form_data)
        if r.status_code != 200:
            raise UpdateMyDnsJpError("Abnormal response from MyDNS.JP web. (Confirm DomainInfo)")
        return None

    def _get_form_element(self, text: str, target: str) -> dict:
        """
        Extract form parameter elements from html.

        :param text: html text
        :param target: action of target form.

        :return: element dictionary of target form
        """
        result = None
        pos_form=0
        while pos_form < len(text):
            regexp_form_result = regexp_form.search(text[pos_form:])
            if regexp_form_result is None:
                break
            pos_form += regexp_form_result.end()
            regexp_action_result = regexp_action.search(regexp_form_result[1])
            if regexp_action_result is None:
                continue
            regexp_method_result = regexp_method.search(regexp_form_result[1])
            if regexp_method_result is None:
                continue
            if regexp_action_result[1] != target:
                continue
            if result is None:
                result = {}
            name = ""
            type = "form"
            action = regexp_action_result[1]
            method = regexp_method_result[1]
            result[name] = {}
            result[name]["type"] = type
            result[name]["action"] = action
            result[name]["method"] = method
            pos_input = 0
            while pos_input < len(regexp_form_result[2]):
                regexp_input_result = regexp_input.search(regexp_form_result[2][pos_input:])
                if regexp_input_result is None:
                    break
                pos_input += regexp_input_result.end()
                regexp_type_result = regexp_type.search(regexp_input_result[1])
                if regexp_type_result is None:
                    continue
                regexp_name_result = regexp_name.search(regexp_input_result[1])
                if regexp_name_result is None:
                    continue
                regexp_value_result = regexp_value.search(regexp_input_result[1])
                if regexp_value_result is None:
                    continue
                type = regexp_type_result[1]
                name = regexp_name_result[1]
                value = regexp_value_result[1]
                result[name] = {}
                result[name]["type"] = type
                result[name]["value"] = value
            pos_select = 0
            while pos_select < len(regexp_form_result[2]):
                regexp_select_result = regexp_select.search(regexp_form_result[2][pos_select:])
                if regexp_select_result is None:
                    break
                pos_select += regexp_select_result.end()
                type = "select"
                regexp_name_result = regexp_name.search(regexp_select_result[1])
                if regexp_name_result is None:
                    continue
                name = regexp_name_result[1]
                result[name] = {}
                result[name]["type"] = type
                result[name]["option"] = []
                pos_option = 0
                while pos_option < len(regexp_select_result[2]):
                    regexp_option_result = regexp_option.search(regexp_select_result[2][pos_option:])
                    if regexp_option_result is None:
                        break
                    pos_option += regexp_option_result.end()
                    regexp_value_result = regexp_value.search(regexp_option_result[1])
                    if regexp_value_result is None:
                        continue
                    value = regexp_value_result[1]
                    result[name]["option"].append(value)
                    regexp_selected_result = regexp_selected.search(regexp_option_result[1])
                    if regexp_selected_result is None:
                        continue
                    result[name]["value"] = value
        return result

    def _get_form_data(self, element: dict, except_names: list) -> dict:
        """
        Convert to sending data from parameter element.

        :param element: element dictionary of form
        :param except_names: name list of not to send.

        :return: sending data
        """
        result = None
        for name, param in element.items():
            if name == "":
                continue
            if "value" not in param:
                continue
            if except_names is not None and name in except_names:
                continue
            if result is None:
                result = {}
            result[name] = param["value"]
        return result

    def _get_domaininame_element(self, element: dict) -> dict:
        """
        Get domainname element from element dictionary.

        :param element: element dictionary of form

        :return: domainname element
        """
        if NAME_OF_MYDNSJP_DOMAINNAME not in element:
            return None
        return element[NAME_OF_MYDNSJP_DOMAINNAME]

    def _get_mx_element(self, element: dict) -> dict:
        """
        Get mx element from element dictionary.

        :param element: element dictionary of form

        :return: mx element dictionary
        """
        result = None
        for name, param in element.items():
            if name == "":
                continue
            if "value" not in param:
                continue
            regexp_name_of_mydnsjp_dnsinfo_result = regexp_name_of_mydnsjp_dnsinfo.search(name)
            if regexp_name_of_mydnsjp_dnsinfo_result is None:
                continue
            key = regexp_name_of_mydnsjp_dnsinfo_result[1]
            ix = regexp_name_of_mydnsjp_dnsinfo_result[2]
            value = param["value"]
            if key not in KEYS_OF_MYDNSJP_MX:
                continue
            if result is None:
                result = {}
            if ix not in result:
                result[ix] = {}
            result[ix][key] = param
        return result

    def _get_record_element(self, element: dict) -> dict:
        """
        Get record element from element dictionary.

        :param element: element dictionary of form

        :return: record element dictionary
        """
        result = None
        for name, param in element.items():
            if name == "":
                continue
            if "value" not in param:
                continue
            regexp_name_of_mydnsjp_dnsinfo_result = regexp_name_of_mydnsjp_dnsinfo.search(name)
            if regexp_name_of_mydnsjp_dnsinfo_result is None:
                continue
            key = regexp_name_of_mydnsjp_dnsinfo_result[1]
            ix = regexp_name_of_mydnsjp_dnsinfo_result[2]
            value = param["value"]
            if key not in KEYS_OF_MYDNSJP_RECORD:
                continue
            if result is None:
                result = {}
            if ix not in result:
                result[ix] = {}
            result[ix][key] = param
        return result

    def _find_record_element(self, record: dict, hostname: str, type: str, content: str) -> dict:
        """
        Find record element from record dictionary.

        :param record: record dictionary
        :param hostname: search hostname or None
        :param type: search type or None
        :param content: search content or None

        :return: record element dictionary
        """
        result = None
        for key, param in record.items():
            if hostname is not None and param["hostname"]["value"] != hostname:
                continue
            if type is not None and param["type"]["value"] != type:
                continue
            if content is not None and param["content"]["value"] != content:
                continue
            if result is None:
                result = {}
            result[key] = param
        return result
