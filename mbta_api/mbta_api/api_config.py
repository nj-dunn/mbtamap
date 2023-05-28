import netrc
import os
import logging
from typing import Optional


class ApiAuthenticationMethod:
    _header: str = ""
    _value: str = ""

    @property
    def http_header(self):
        return self._header

    @property
    def value(self):
        return self._value


class ApiKey(ApiAuthenticationMethod):
    def __init__(self, key_value: str):
        self._header = "x-api-key"
        self._value = key_value


class ApiConfig:
    @property
    def url(self):
        return self._url

    @property
    def auth(self) -> ApiAuthenticationMethod:
        return self._auth

    def __init__(self, url, auth: Optional[ApiAuthenticationMethod] = None):
        self._url = url
        self._auth = auth

    @classmethod
    def from_netrc(cls, path=""):
        if not path:
            path = os.path.join(os.getenv["HOME"], ".netrc")

        try:
            netrc_file = netrc.netrc(path)
        except Exception as e:
            logging.fatal(f"Could not open netrc credential file at {path}")
