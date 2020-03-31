from abc import ABC, abstractmethod
from typing import Generator, List, Union, Tuple

from geomdl import fitting, BSpline
import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import spatial
from skimage.feature import hog

from server.analysis import Size, Rect, Point, RoiMaker


class ImageOperation(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)

    @abstractmethod
    def update(self, input_image: np.ndarray) -> np.ndarray:
        pass


class Gui:
    _operations: List[ImageOperation]

    def __init__(self):
        window_size = (1920 // 2, 1080 // 2)
        window_name = "image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.createTrackbar("parking_width", window_name, 0, 400, lambda a: print(a))
        cv2.resizeWindow(window_name, *window_size)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        self._operations = []
        self.image = cv2.imread("test.bmp")
        self.destination_size = Size(512, 256)
        self.roi_maker = RoiMaker(self.image, self.destination_size)
        self.polygon_of_interest = [
            vertex for vertex in Rect(Point(100, 100), self.destination_size).vertices()
        ]
        self.input_image = None
        self.output_image = None
        self.mouse_click_counter = 0
        self.mouse_position = Point(0, 0)

        curves_points = [
            [Point(x=408, y=73), Point(x=416, y=131), Point(x=456, y=182), Point(x=576, y=206), Point(x=850, y=192),
             Point(x=1122, y=184), Point(x=1472, y=206), Point(x=1676, y=220), Point(x=1728, y=220)],

            [Point(x=308, y=73), Point(x=308, y=160), Point(x=350, y=250), Point(x=464, y=315), Point(x=666, y=335),
             Point(x=1100, y=337), Point(x=1400, y=345), Point(x=1740, y=343)]
        ]

        self.curves = []
        for curve_points in curves_points:
            curve = Curve(1000)
            curve.add_points(curve_points)
            self.curves.append(curve)

    def add_operation(self, operation: ImageOperation):
        self._operations.append(operation)

    def run(self):
        rtsp_url = "rtsp://admin:123@192.168.1.106:554/onvif1"
        capture = cv2.VideoCapture(
            f"rtspsrc location=\"{rtsp_url}\" ! rtph264depay ! h264parse ! avdec_h264 ! autovideoconvert ! appsink",
            cv2.CAP_GSTREAMER
        )
        while True:
            result, frame = capture.read()
            if result:
                np.copyto(self.image, frame)

            self.calculate()
            self.draw()

            image = np.copy(self.output_image)
            for window in self._operations:
                image = window.update(image)
                cv2.imshow(window.name, image)
                cv2.resizeWindow(window.name, image.shape[1], image.shape[0])

            if cv2.waitKey(100) == ord("q"):
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

        first_curve = self.curves[0]
        _, t = first_curve.closest_point(self.mouse_position)

        for curve in self.curves:
            curve.draw(image)
            related_point = curve.evaluate(t)
            cv2.circle(image, related_point.to_tuple(), 8, (0, 0, 255), cv2.FILLED)

        cv2.imshow("input", self.input_image)
        cv2.imshow("output", self.output_image)
        cv2.imshow("image", image)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            point_index = self.mouse_click_counter % len(self.polygon_of_interest)
            self.polygon_of_interest[point_index] = Point(x, y)
            print(self.polygon_of_interest)
            self.mouse_click_counter += 1

        if event == cv2.EVENT_RBUTTONDOWN:
            pass  # self.curves.append(Curve(1000))

        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_position = Point(x, y)


class Curve:
    curve_points: np.ndarray
    curve: Union[None, BSpline.Curve]
    points: List[Point]

    def __init__(self, samples: int):
        self.points = []
        self.curve_points = np.empty((0, 2), dtype=np.float32)
        self.curve = None
        self.kd = None
        self.samples = samples
        self.t = np.empty((0,), dtype=np.float32)

    def add_point(self, point: Point) -> None:
        self.points.append(point)
        self._recalculate()

    def add_points(self, points: List[Point]) -> None:
        self.points.extend(points)
        self._recalculate()

    def _recalculate(self) -> None:
        if len(self.points) >= 3:
            self.t = np.linspace(0, 1, num=self.samples, endpoint=True)
            print(self.t.shape)
            self.curve = fitting.interpolate_curve(
                [point.to_tuple() for point in self.points], 2
            )
            self.curve_points = np.array(
                self.curve.evaluate_list(self.t)
            ).astype(np.int32).reshape((-1, 2))
            self.kd = spatial.KDTree(self.curve_points)

    def clear_points(self) -> None:
        self.points.clear()
        self.curve_points = np.empty((2, 0), dtype=np.float32)
        self.curve = None
        self.kd = None

    def closest_point(self, point: Point) -> Tuple[Point, float]:
        if len(self.points) < 3:
            return Point(0, 0), 0.0

        _, closest_index = self.kd.query(point.to_tuple())
        return Point(*self.curve_points[closest_index]), self.t[closest_index]

    def evaluate(self, t: float) -> Point:
        index = int(np.clip(t * self.samples, 0, self.samples - 1))
        return Point(*self.curve_points[index])

    def draw(self, image: np.ndarray) -> None:
        for point in self.points:
            cv2.circle(image, point.to_tuple(), 5, (255, 0, 0), cv2.FILLED)
        cv2.polylines(image, [self.curve_points], False, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)


class BlurOperation(ImageOperation):
    def update(self, image: np.ndarray) -> np.ndarray:
        return cv2.blur(image, (7, 7))


class FeaturesOperation(ImageOperation):
    def __init__(self):
        super().__init__()
        plt.ion()
        plt.show()

    def update(self, image: np.ndarray) -> np.ndarray:
        # blurred_image = cv2.GaussianBlur(image, (9, 9), 2.0)
        fd, feature_image = hog(image, orientations=8, pixels_per_cell=(8, 8),
                                cells_per_block=(1, 1), visualize=True, multichannel=True)
        # feature_image = local_binary_pattern(bw_image, 8 * 3, 3, "default")

        plt.subplot(211)
        plt.imshow(image)
        plt.subplot(212)
        plt.imshow(feature_image)
        plt.pause(0.001)

        return image


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


def main():
    gui = Gui()
    # gui.add_operation(BlurOperation())
    # gui.add_operation(FeaturesOperation())
    gui.run()


if __name__ == '__main__':
    main()
