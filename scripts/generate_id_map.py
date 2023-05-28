from mbta_api import MBTASubwayApi
import json
import logging

api = MBTASubwayApi.from_netrc()

with open("data/mappoints.json", "r") as f:
    data = json.load(f)
mappoints = {}
for mappoint in data:
    mappoints[mappoint["name"]] = mappoint


stops = api.get_stops()

id_list = []
for stop in stops:
    if stop.name in mappoints.keys():
        id_list.append(
            {
                "mapid": mappoints[stop.name]["mapid"],
                "id": stop.id,
            }
        )
    else:
        logging.fatal(f"Unknown stop name {stop.name}!! Map may be out of date")

id_list = sorted(id_list, key=lambda x: int(x["id"]))

with open("data/stops.json", "w") as f:
    json.dump(id_list, f, indent=4)
