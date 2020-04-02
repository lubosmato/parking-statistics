import logging
import time
from threading import Thread
from typing import Dict, Set, Optional

import cv2
import numpy as np

from server.analysis.compressor import Compressor
from server.analysis.roi_maker import RoiMaker
from server.analysis.types import Point, Size
from server.server import MjpegStream

logger = logging.getLogger(__name__)


class ImageAnalyzer(Thread):
    _streams: Dict[str, Optional[MjpegStream]]
    _compressors: Dict[str, Compressor]

    def __init__(self):
        super().__init__()

        self.roi_size = Size(512, 256)
        self.camera_size = Size(1920 // 2, 1080 // 2)
        self.poi = [
            Point(0, 0),
            Point(self.camera_size.width - 1, 0),
            Point(self.camera_size.width - 1, self.camera_size.height - 1),
            Point(0, self.camera_size.height - 1),
        ]
        self._is_running = False
        self._camera_image = np.empty((1, 1, 3), dtype=np.uint8)

        self._output_images_names = {"main", "roi"}

        self._analysis_output_images = {
            name: np.empty((1, 1, 3), dtype=np.uint8)
            for name in self._output_images_names
        }
        self._compressors = {
            name: Compressor()
            for name in self._output_images_names
        }
        self._streams = {
            name: None
            for name in self._output_images_names
        }

        self._camera_fps = 10
        rtsp_url = "rtsp://admin:123@192.168.1.106:554/onvif1"
        gstreamer_pipeline = f"rtspsrc location=\"{rtsp_url}\" ! rtph264depay ! h264parse ! avdec_h264 ! "
        gstreamer_pipeline += f"autovideoconvert ! videorate ! video/x-raw,framerate={self._camera_fps}/1 ! appsink"

        logger.info("Starting camera capture")
        logger.info(f"Using GStreamer pipeline: '{gstreamer_pipeline}'")

        self._camera = cv2.VideoCapture(
            gstreamer_pipeline,
            cv2.CAP_GSTREAMER
        )

    @property
    def output_images_names(self) -> Set[str]:
        return self._output_images_names

    def assign_stream(self, name: str, stream: MjpegStream) -> None:
        self._streams[name] = stream

    def start(self):
        self._is_running = True
        for compressor in self._compressors.values():
            compressor.start()
        super().start()

    def stop(self):
        self._is_running = False
        self.join()
        for compressor in self._compressors.values():
            compressor.stop()

    def run(self) -> None:
        debug = False

        start_time = time.time()
        log_fps_every = 100  # every 100 frame
        frame_count = 0
        while self._is_running:
            result, frame = self._camera.read()
            if result:
                self._camera_image = cv2.resize(frame, self.camera_size.to_tuple())

                self._analyze()
                self._compress()
                self._stream()

                if debug:
                    frame_count += 1
                    if frame_count % log_fps_every == 0:
                        time_delta = (time.time() - start_time)
                        if time_delta == 0:
                            true_fps = 0
                        else:
                            true_fps = log_fps_every / time_delta
                        logger.info(f"Camera FPS is {true_fps:.2f}")
                        start_time = time.time()
            else:
                logger.warning(f"Skipped frame, result: {result}")
                time.sleep(1 / self._camera_fps)

    def _analyze(self) -> None:
        self._analysis_output_images["main"] = self._camera_image
        self._make_roi()

    def _make_roi(self):
        roi_maker = RoiMaker(self._camera_image, self.roi_size)
        self._analysis_output_images["roi"] = roi_maker.roi(self.poi)

    def _compress(self) -> None:
        for name, image in self._analysis_output_images.items():
            self._compressors[name].input_queue.put(image)

    def _stream(self) -> None:
        for name, compressor in self._compressors.items():
            stream_data = compressor.output_queue.get()
            stream = self._streams[name]
            if stream is not None:
                stream.raw_image_data = stream_data
