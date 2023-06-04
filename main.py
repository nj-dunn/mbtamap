# import urequests
# import argparse
import netrc
import os
import logging
from PIL import Image, ImageTk
import tkinter
from tkinter import Tk
from tkinter import ttk
from mbta_api import World, MBTASubwayApi
import mbta_api
import json
import time


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(
        round(x - r), round(y - r), round(x + r), round(y + r), **kwargs
    )


class MapPoint:
    def __init__(self, name, color=0x000000, intensity=1.0):
        self._name = name
        self._color = color
        self._intensity = intensity

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value


class MBTAMap:
    def __init__(self):
        self.root = Tk()
        map_image = Image.open(
            os.path.join(os.path.dirname(__file__), "data/images/mbta-subway-map.png")
        )
        print("Loading subway image.")
        print(f"Height: {map_image.height}")
        print(f"Width:  {map_image.width}")

        self.original_world = World(map_image)
        self.original_station_diameter = 44
        self.scaled_world = self.original_world.resize(800, 800)
        self.tk_image = ImageTk.PhotoImage(self.scaled_world.image)
        with open("data/stops.json", "r") as f:
            stations = json.load(f)

        # Convert MBTA ID of a stop into a single ID representing a point on the map
        # Multiple MBTA stops map to a single point
        self._id_map = {}
        for station in stations:
            self._id_map[station["id"]] = station["mapid"]
        with open("data/mappoints.json", "r") as f:
            mappoints = json.load(f)
        self._mappoints = {}
        self._coordinates = {}
        for mappoint in mappoints:
            self._mappoints[mappoint["mapid"]] = MapPoint(mappoint["name"])
            self._coordinates[mappoint["mapid"]] = mappoint["coords"]
        self.canvas = tkinter.Canvas(
            self.root,
            width=self.scaled_world.width,
            height=self.scaled_world.height,
            bg="black",
        )
        self.canvas.grid()

    def turn_off_all(self):
        new_state = {}
        for id, point in self._mappoints.items():
            point.color = 0x000000
            point.intensity = "0.0"
            new_state[id] = point
        self._mappoints = new_state

    def update(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tkinter.constants.NW)
        for id, point in self._mappoints.items():
            scaled_coords = self.original_world.transformTo(
                self._coordinates[id], self.scaled_world
            )
            scaled_diameter = self.original_world.transformTo(
                (self.original_station_diameter, 0), self.scaled_world
            )[0]

            self.canvas.create_circle(
                scaled_coords[0],
                scaled_coords[1],
                scaled_diameter / 2,
                fill="#{:06x}".format(point.color),
            )

        self.canvas.pack()
        self.root.update_idletasks()
        self.root.update()

    def get_mapid(self, mbta_id):
        if mbta_id not in self._id_map:
            return None
        return self._id_map[mbta_id]

    def get_mappoint(self, id):
        return self._mappoints[id]

    def update_mappoint(self, id, color, intensity):
        """
        Updates Map ID to specified color and brightness
        """
        self._mappoints[id].color = color
        self._mappoints[id].intensity = intensity


class BaseController:
    def __init__(self, map_type):
        self.mbta_map: MBTAMap = map_type()

    def draw_loop(self, count, vehicles: mbta_api.Vehicle):
        raise NotImplementedError()


class SimpleController(BaseController):
    def draw_loop(self, count, vehicles):
        self.mbta_map.turn_off_all()
        for vehicle in vehicles:
            if not vehicle.stop or not vehicle.stop.isdigit():
                # There's some weird stops at the ends of lines like "Oak-Grove-02. Maybe an intermediate state before it turns around"
                # also the stop may potentially be None - if the vehicle is out of service
                continue
            if vehicle.direction:
                color = 0xFF0000
            else:
                color = 0x00FF00

            local_id = self.mbta_map.get_mapid(vehicle.stop)
            if not local_id:
                logging.error(f"Unmapped MBTA ID {vehicle.stop}")
                continue

            current_mappoint = self.mbta_map.get_mappoint(local_id)
            color = color | current_mappoint.color

            if vehicle.status == mbta_api.Vehicle.Status.STOPPED_AT:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
            elif count %2:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
        self.mbta_map.update()


class AlternatingController(BaseController):
    def draw_loop(self, count, vehicles):
        self.mbta_map.turn_off_all()
        for vehicle in vehicles:
            if not vehicle.stop or not vehicle.stop.isdigit():
                # There's some weird stops at the ends of lines like "Oak-Grove-02. Maybe an intermediate state before it turns around"
                # also the stop may potentially be None - if the vehicle is out of service
                continue

            if vehicle.direction:
                if count % 10 < 5:
                    color = 0xFF0000
                else:
                    continue
            else:
                if count % 10 >= 5:
                    color = 0x00FF00
                else:
                    continue

            local_id = self.mbta_map.get_mapid(vehicle.stop)
            if not local_id:
                logging.error(f"Unmapped MBTA ID {vehicle.stop}")
                continue

            current_mappoint = self.mbta_map.get_mappoint(local_id)
            color = color | current_mappoint.color

            if vehicle.status == mbta_api.Vehicle.Status.STOPPED_AT:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
            else:
                self.mbta_map.update_mappoint(local_id, 0xFFFF00, 1.0)
        self.mbta_map.update()

class ZenController(BaseController):
    def draw_loop(self, count, vehicles):
        raise NotImplementedError()


if __name__ == "__main__":
    tkinter.Canvas.create_circle = _create_circle
    try:
        api = MBTASubwayApi.from_netrc()
    except Exception as e:
        logging.error(str(e))
        api = MBTASubwayApi(None)

    ticks = 0
    freq = 1

    controller = AlternatingController(MBTAMap)

    while 1:
        vehicles = api.get_vehicles()
        controller.draw_loop(ticks, vehicles)
        ticks = ticks + 1
        time.sleep(freq)

    input("Press Enter to continue...")
