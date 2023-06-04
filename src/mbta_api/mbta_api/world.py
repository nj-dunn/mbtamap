from PIL import Image

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
