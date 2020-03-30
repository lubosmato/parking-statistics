from dataclasses import dataclass
from typing import Tuple, Generator

import numpy as np
import cv2


@dataclass
class Point:
    x: int
    y: int

    def to_tuple(self) -> Tuple[int, int]:
        return self.x, self.y


@dataclass
class Size:
    width: int
    height: int

    def to_tuple(self) -> Tuple[int, int]:
        return self.width, self.height

    def np_slice(self) -> Tuple[slice, slice]:
        return slice(0, self.height), slice(0, self.width)


@dataclass
class Rect:
    start: Point
    size: Size

    @staticmethod
    def from_cv_rect(cv_rect: Tuple[int, int, int, int]) -> "Rect":
        return Rect(Point(*cv_rect[0:2]), Size(*cv_rect[2:4]))

    def roi(self) -> Tuple[Point, Point]:
        return self.start, Point(self.start.x + self.size.width, self.start.y + self.size.height)

    def vertices(self) -> Tuple[Point, Point, Point, Point]:
        return self.start, \
               Point(self.start.x + self.size.width, self.start.y), \
               Point(self.start.x + self.size.width, self.start.y + self.size.height), \
               Point(self.start.x, self.start.y + self.size.height)

    def draw_into(self, img: np.ndarray, color: Tuple[int, int, int], thickness=1):
        p1, p2 = self.roi()
        cv2.rectangle(img, p1.to_tuple(), p2.to_tuple(), color, thickness=thickness, lineType=cv2.LINE_AA)

    def np_slice(self) -> Tuple[slice, slice]:
        return slice(self.start.y, self.start.y + self.size.height), slice(self.start.x, self.start.x + self.size.width)


class RoiMaker:
    _image: np.ndarray

    def __init__(self, image: np.ndarray, output_size: Size):
        self._image = image
        self._image_size = Size(self._image.shape[1], self._image.shape[0])
        self._output_size = output_size
        output_rectangle = Rect(Point(0, 0), output_size)
        self._output_polygon = np.array([vertex.to_tuple() for vertex in output_rectangle.vertices()], dtype=np.float32)

    def roi(self, polygon_of_interest: Tuple[Point, Point, Point, Point]):
        points = [[p.x, p.y] for p in polygon_of_interest]
        input_polygon = np.array(points, dtype=np.float32)
        m = cv2.getPerspectiveTransform(input_polygon, self._output_polygon)
        return cv2.warpPerspective(self._image, m, self._image_size.to_tuple())[self._output_size.np_slice()]
