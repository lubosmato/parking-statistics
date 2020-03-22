import os
from multiprocessing import Process
from server.server import run

if __name__ == '__main__':
    # env var OPENCV_FFMPEG_CAPTURE_OPTIONS is ignored when opencv runs in same process
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    p = Process(target=run)
    p.start()
    p.join()
