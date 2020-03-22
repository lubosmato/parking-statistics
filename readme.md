# Parking Statistics
One day I was wondering how to optimize my daily routine. And thought that searching for a parking place takes me about 15 minutes a day. For that time I could be playing my favourite video game or coding something great.

So I installed an IP camera I bought few years ago to building's roof in order to see parking places. The camera is very cheap chinese brand camera: [Ebay link](https://www.ebay.com/itm/Security-Wireless-WIFI-IP-Audio-Camera-HD-IR-1080P-Outdoor-TF-card-slot-yoosee/323296406638). Setting up the camera wasn't complicated and after few minutes of googling I found that the camera streams its main stream on RTSP protocol on url `rtsp://admin:123@192.168.1.106/onvif1`.

# Reading Camera Stream
When I tried to connect to the stream with OpenCV in Python I run into problems. The camera uses UDP protocol and OpenCV uses TCP as a default. But I was lucky that OpenCV added an option to provide custom settings via environment variable, see [OpenCV FFMPEG open](https://github.com/opencv/opencv/blob/master/modules/videoio/src/cap_ffmpeg_impl.hpp#L911). So I set env var `OPENCV_FFMPEG_CAPTURE_OPTIONS` to `rtsp_transport;udp` in Python but somehow OpenCV ignored this new value. Luckily I found a workaround and was able to get frames from the camera.
