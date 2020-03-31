from multiprocessing import Value
from queue import Queue

import cv2


def _run(input_image_queue: Queue, output_compressed_queue: Queue, is_running: Value):
    while bool(is_running.value):
        image = input_image_queue.get()
        _, buff = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 100])
        output_compressed_queue.put(bytearray(buff))
