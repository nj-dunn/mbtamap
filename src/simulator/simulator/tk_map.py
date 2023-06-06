from PIL import Image, ImageTk
import tkinter
from tkinter import Tk
from tkinter import ttk
import json
from mbta_api import BaseMap, TkMapPoint


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(
        round(x - r), round(y - r), round(x + r), round(y + r), **kwargs
    )
tkinter.Canvas.create_circle = _create_circle

class World:
    # Initialize the world with a background image
    def __init__(self, img: Image):
        self._image = img

    @property
    def width(self):
        return self._image.width

    @property
    def height(self):
        return self._image.height

    def resize(self, x_coord, y_coord):
        new_image = self._image.resize((x_coord, y_coord))
        return World(new_image)

    @property
    def image(self):
        return self._image

    def transformTo(self, coordinate, other_space):
        x_ratio = other_space.width / self.width
        y_ratio = other_space.height / self.height
        return (coordinate[0] * x_ratio, coordinate[1] * y_ratio)

class TkMapConfig:
    map_image_path = ""
    id_mapping_json = ""
    mappoints_json = ""

class TkMap(BaseMap):
    def __init__(self, config):
        self.root = Tk()
        map_image = Image.open(
            config.map_image_path
        )
        print("Loading subway image.")
        print(f"Height: {map_image.height}")
        print(f"Width:  {map_image.width}")

        self.original_world = World(map_image)
        self.original_station_diameter = 44
        self.scaled_world = self.original_world.resize(800, 800)
        self.tk_image = ImageTk.PhotoImage(self.scaled_world.image)
        with open(config.id_mapping_json, "r") as f:
            stations = json.load(f)

        # Convert MBTA ID of a stop into a single ID representing a point on the map
        # Multiple MBTA stops map to a single point
        id_map = {}
        for station in stations:
            id_map[station["id"]] = station["mapid"]
        with open(config.mappoints_json, "r") as f:
            mappoint_data = json.load(f)
        mappoints = [TkMapPoint(mp["mapid"], mp["name"], mp["coords"]) for mp in mappoint_data]

        super().__init__(mappoints, id_map)

        self.canvas = tkinter.Canvas(
            self.root,
            width=self.scaled_world.width,
            height=self.scaled_world.height,
            bg="black",
        )
        self.canvas.grid()

    def update(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tkinter.constants.NW)
        for _, point in self._mappoints.items():
            scaled_coords = self.original_world.transformTo(
                point.coordinate, self.scaled_world
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