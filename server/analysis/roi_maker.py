import logging
from typing import Tuple, Iterable
import cv2
import numpy as np

from server.analysis.types import Size, Point, Rectangle

logger = logging.getLogger(__name__)


class RoiMaker:
    _image: np.ndarray

    def __init__(self, image: np.ndarray, output_size: Size):
        self._image = image
        self._image_size = Size(self._image.shape[1], self._image.shape[0])
        self._output_size = output_size
        output_rectangle = Rectangle(Point(0, 0), output_size)
        self._output_polygon = np.array([vertex.to_tuple() for vertex in output_rectangle.vertices()], dtype=np.float32)

    def roi(self, polygon_of_interest: Iterable[Point]) -> np.ndarray:
        points = [[p.x, p.y] for p in polygon_of_interest]
        input_polygon = np.array(points, dtype=np.float32)
        m = cv2.getPerspectiveTransform(input_polygon, self._output_polygon)
        return cv2.warpPerspective(self._image, m, self._image_size.to_tuple())[self._output_size.np_slice()]
