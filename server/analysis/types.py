from dataclasses import dataclass
from typing import Tuple

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
class Rectangle:
    top_left: Point
    size: Size

    @staticmethod
    def from_cv_rect(cv_rect: Tuple[int, int, int, int]) -> "Rectangle":
        return Rectangle(Point(*cv_rect[0:2]), Size(*cv_rect[2:4]))

    def roi(self) -> Tuple[Point, Point]:
        return self.top_left, Point(self.top_left.x + self.size.width, self.top_left.y + self.size.height)

    def vertices(self) -> Tuple[Point, Point, Point, Point]:
        return self.top_left, \
               Point(self.top_left.x + self.size.width, self.top_left.y), \
               Point(self.top_left.x + self.size.width, self.top_left.y + self.size.height), \
               Point(self.top_left.x, self.top_left.y + self.size.height)

    def draw_into(self, img: np.ndarray, color: Tuple[int, int, int], thickness=1):
        p1, p2 = self.roi()
        cv2.rectangle(img, p1.to_tuple(), p2.to_tuple(), color, thickness=thickness, lineType=cv2.LINE_AA)

    def np_slice(self) -> Tuple[slice, slice]:
        return slice(self.top_left.y, self.top_left.y + self.size.height), slice(self.top_left.x, self.top_left.x + self.size.width)
