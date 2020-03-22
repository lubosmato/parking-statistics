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


class RoiGui:
    def __init__(self):
        window_size = (1920 // 2, 1080 // 2)
        window_name = "image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, *window_size)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        self.image = cv2.imread("test.bmp")
        destination_size = Size(512, 256)
        self.roi_maker = RoiMaker(self.image, destination_size)
        self.polygon_of_interest = [
            vertex for vertex in Rect(Point(100, 100), destination_size).vertices()
        ]
        self.input_image = None
        self.output_image = None
        self.mouse_click_counter = 0

    def run(self):
        while True:
            self.calculate()
            self.draw()

            if cv2.waitKey(int(1 / 60 * 1000)) == ord("q"):
                break
        cv2.destroyAllWindows()

    def calculate(self):
        input_mask = np.zeros((*self.image.shape[:2], 1), dtype=np.uint8)
        input_polygon = np.array([[p.x, p.y] for p in self.polygon_of_interest], dtype=np.int32)
        cv2.fillPoly(input_mask, [input_polygon], (255, 255, 255))

        input_image = cv2.bitwise_and(self.image, self.image, mask=input_mask)
        input_roi = Rect.from_cv_rect(cv2.boundingRect(input_mask))
        self.input_image = input_image[input_roi.np_slice()]
        self.output_image = self.roi_maker.roi(tuple(self.polygon_of_interest)[0:4])

    def draw(self):
        image = self.image.copy()
        polygon = np.array([[p.x, p.y] for p in self.polygon_of_interest], dtype=np.int32)
        cv2.polylines(image, [polygon], True, (255, 255, 255), 3, cv2.LINE_AA)
        current_point = self.polygon_of_interest[self.mouse_click_counter % len(self.polygon_of_interest)]
        cv2.circle(image, current_point.to_tuple(), 10, (0, 0, 255), cv2.FILLED)

        cv2.imshow("input", self.input_image)
        cv2.imshow("output", self.output_image)
        cv2.imshow("image", image)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            point_index = self.mouse_click_counter
            self.polygon_of_interest[point_index % len(self.polygon_of_interest)] = Point(x, y)
            self.mouse_click_counter += 1


def run():
    RoiGui().run()


def horizontal_window_sequence(size: Size, start: int, end: int, steps: int) -> Generator[Rect, None, None]:
    if steps <= 0:
        raise ValueError("steps must be greater than 0")

    roi = Rect(Point(0, 0), size)
    delta_x = (end - start) / steps

    new_start_x = start

    for _ in range(steps - 1):
        yield roi
        new_start_x += delta_x
        roi.start.x = int(new_start_x)


def _run():
    window_size = (1920 // 2, 1080 // 2)
    window_name = "video"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, *window_size)
    capture = cv2.VideoCapture("rtsp://admin:123@192.168.1.106/onvif1", cv2.CAP_FFMPEG)
    while True:
        result, frame = capture.read()
        cv2.imshow(window_name, frame)

        if cv2.waitKey(16) == ord("q"):
            break

    cv2.destroyAllWindows()
