import numpy as np
from multiprocessing import Queue, Value, Process

from server.analysis.compressor._run import _run


class Compressor:
    def __init__(self):
        self._is_running = Value("i", False)
        self._input_image_queue = Queue()
        self._output_image_queue = Queue()
        self._process = None

    def start(self):
        self._process = Process(
            target=_run,
            args=(self._input_image_queue, self._output_image_queue, self._is_running)
        )
        self._is_running.value = True
        self._process.start()

    def stop(self):
        if self._process is None:
            raise AttributeError("Compressor did not start yet, cannot stop")

        self._is_running.value = False
        self._input_image_queue.put(np.empty((1, 1, 3), dtype=np.uint8))
        self._process.join()

    @property
    def input_queue(self) -> Queue:
        return self._input_image_queue

    @property
    def output_queue(self) -> Queue:
        return self._output_image_queue
