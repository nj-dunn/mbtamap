from .api_config import ApiConfig, ApiKey
import requests
from typing import Dict, Optional, List
import logging
import urllib.parse
import enum
import os
import netrc


class HTTPError(Exception):
    def __init__(self, url, code, msg):
        self._url = url
        self._code = code
        self._msg = msg

    def __str__(self):
        return f"{self._code}: {self._msg}"


class ApiBase:
    def __init__(self, config: ApiConfig):
        self._config: ApiConfig = config

    def urlencode(s: str) -> str:
        s = s.replace("[", "%5")

    def get(self, path: str, query_params: Dict[str, str] = {}):
        headers = {}
        if self._config.auth:
            headers[self._config.auth.http_header] = self._config.auth.value

        if query_params:
            path += "?" + "&".join(
                [f"{key}={value}" for key, value in query_params.items()]
            )

        # MBTA API doesn't seem to handle URL encoded '='
        url = "/".join([self._config.url, urllib.parse.quote(path, safe="=?")])
        logging.debug(f"GET: {url}")
        response = requests.get(url, headers=headers)

        if not response.ok:
            logging.error(f"Received response: {response.status_code}: {response.text}")
            raise HTTPError(url, code=response.status_code, msg=response.text)

        return response


class Stop:
    def __init__(self, data):
        self._id = data["id"]
        self._name = data["attributes"]["name"]
        self._latitude = data["attributes"]["latitude"]
        self._longitude = data["attributes"]["longitude"]

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name


class Vehicle:
    class Status(enum.IntEnum):
        INCOMING_AT = 0
        STOPPED_AT = 1
        IN_TRANSIT_TO = 2

        @classmethod
        def from_string(cls, s: str):
            if "INCOMING_AT" in s:
                return cls.INCOMING_AT
            elif "STOPPED_AT" in s:
                return cls.STOPPED_AT
            elif "IN_TRANSIT_TO" in s:
                return cls.IN_TRANSIT_TO
            else:
                raise Exception(f"Invalid value {s}")

    def __init__(self, data):
        self._id = data["id"]
        self._status = self.Status.from_string(data["attributes"]["current_status"])
        self._direction = data["attributes"]["direction_id"]
        self._route_id = data["relationships"]["route"]["data"]["id"]
        # For vehicles, current stop sequence may be returned as null, as well as the stop
        # relationship. Perhaps means train is out of service?
        if data["relationships"]["stop"]["data"]:
            self._stop = data["relationships"]["stop"]["data"]["id"]
        else:
            self._stop = None

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def direction(self):
        return self._direction

    @property
    def route_id(self):
        return self._route_id

    @property
    def stop(self):
        return self._stop


class MBTASubwayApi(ApiBase):

    """
    MBTA APIs that are specifically filtered to only deal with Light Rail/
    Metro types (Vehicle types 0 and 1 in GTFS spec):
    https://developers.google.com/transit/gtfs/reference#stopstxt
    """

    def __init__(self, api_key = None):
        super().__init__(ApiConfig("https://api-v3.mbta.com", api_key))

    @classmethod
    def from_netrc(cls, path=""):
        if not path:
            path = os.path.join(os.getenv("HOME"), ".netrc")

        try:
            netrc_file = netrc.netrc(path)
        except FileNotFoundError:
            raise Exception(f"Failed to open netrc at {path}")
        try:
            auth = netrc_file.authenticators("api-v3.mbta.com")
        except Exception as e:
            raise Exception(f"{path} did not have an entry for 'api-v3.mbta.com'")
        return cls(ApiKey(auth[2]))

    def get_vehicles(self):
        try:
            response = self.get("vehicles", query_params={"filter[route_type]": "0,1"})
        except HTTPError:
            return []

        return [Vehicle(entry) for entry in response.json()["data"]]

    def get_vehicle(self, id) -> Optional[Vehicle]:
        try:
            response = self.get(f"vehicles/{id}")
        except HTTPError:
            return None

        return Vehicle(response.json()["data"])

    def get_stops(self) -> List[Stop]:
        try:
            response = self.get("stops", query_params={"filter[route_type]": "0,1"})
        except HTTPError:
            return []

        return [Stop(entry) for entry in response.json()["data"]]
