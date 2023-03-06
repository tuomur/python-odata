import requests
from requests.adapters import HTTPAdapter, Retry

DEFAULT_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def retry_strategy():
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    return retry_strategy


def get_sap_session(url, credentials, default_cookies=None):
    """
    Get sap session with retry strategy
    :param url:
    :param credentials: ("UserName", "Password", "CompanyDB")
    :param default_cookies:
    :return:
    """
    adapter = TimeoutHTTPAdapter(max_retries=retry_strategy())
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if default_cookies is None:
        default_cookies = {"ROUTEID": ".node1"}

    session.request(
        'POST', url + 'Login', json=credentials, cookies=default_cookies,
        verify=False
    )

    return session