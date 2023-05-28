from mbta_api import ApiKey, MBTASubwayApi
import json
import logging
import pytest


@pytest.fixture
def api():
    api = MBTASubwayApi.from_netrc()
    return api


def test_vehicles(api: MBTASubwayApi):
    vehicles = api.get_vehicles()

    # Not sure what the API returns during out-of-service hours
    assert len(vehicles) > 0, "API returns non-zero number of vehicles."

    assert vehicles[0].id


def test_mbta_stations(api: MBTASubwayApi):
    stops = api.get_stops()

    with open("data/stops.json", "r") as f:
        id_map = json.load(f)

    with open("data/mappoints.json", "r") as f:
        mappoints = json.load(f)

    for stop in stops:
        found = False
        for id_map_entry in id_map:
            if stop.id == id_map_entry["id"]:
                found = True
                mapid = id_map_entry["mapid"]
                assert (
                    mappoints[int(mapid)]["name"] == stop.name
                ), "Local Map Data contains matching name from MBTA api"
                break
        assert (
            found
        ), "Stops returned by the API match the local mappings we maintain in-repo"
