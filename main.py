import sys
if "micropython" in sys.implementation.name:
    SYS_MICRO = True
else:
    SYS_MICRO = False

import netrc
import os
import logging
from mbta_api import MBTASubwayApi, AlternatingController
import time

if __name__ == "__main__":
    try:
        api = MBTASubwayApi.from_netrc()
    except Exception as e:
        logging.error(str(e))
        api = MBTASubwayApi(None)

    ticks = 0
    quantum = 1 # seconds

    if not SYS_MICRO:
        from simulator import TkMap, TkMapConfig
        map_type = TkMap
        config = TkMapConfig()
        data_directory = os.path.join(os.path.dirname(__file__), "data")
        config.map_image_path = os.path.join(data_directory, "images/mbta-subway-map.png")
        config.id_mapping_json = os.path.join(data_directory, "stops.json")
        config.mappoints_json = os.path.join(data_directory, "mappoints.json")
    else:
        raise NotImplementedError()

    controller = AlternatingController(map_type, config)

    while 1:
        vehicles = api.get_vehicles()
        controller.draw_loop(ticks, vehicles)
        ticks = ticks + 1
        time.sleep(quantum)

    input("Press Enter to continue...")
