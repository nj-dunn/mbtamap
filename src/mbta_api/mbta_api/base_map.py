from typing import List
from .mappoint import MapPoint

class BaseMap:

    def __init__(self, mps, id_mapping_map):
        self._id_map = id_mapping_map
        self._mappoints = {}
        for mp in mps:
            self._mappoints[mp.id] = mp

    def turn_off_all(self):
        new_state = {}
        for id, point in self._mappoints.items():
            point.color = 0x000000
            point.intensity = "0.0"
            new_state[id] = point
        self._mappoints = new_state

    def update(self):
        # This should be implemented by all subclasses
        # Implementation-defined mechanism to write out mappoint data
        raise NotImplementedError()

    def get_mapid(self, mbta_id):
        """ Given the mbta ID number, return the local map ID"""
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