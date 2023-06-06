class MapPoint:
    def __init__(self, id, name, color=0x000000, intensity=1.0):
        self._id = id
        # Name is only needed for easier logging when something goes wrong
        self._name = name
        self._color = color
        self._intensity = intensity

    @property
    def id(self):
        return self._id

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

class TkMapPoint(MapPoint):
    def __init__(self, id, name, coordinate):
        super().__init__(id, name)
        self._coordinate = coordinate

    @property
    def coordinate(self):
        return self._coordinate


class LEDMapPoint(MapPoint):
    def __init__(self, id, name, pin, offset):

        super().__init__(id, name)
        self._pin = pin
        self._offset = offset