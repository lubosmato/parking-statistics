import cv2
import sys

from PySide2.QtCore import QThread, Signal, Slot
from PySide2.QtGui import QImage, Qt, QPixmap, QCloseEvent, QMouseEvent
from PySide2.QtWidgets import QWidget, QLabel, QApplication, QGridLayout, QStatusBar, QMainWindow


# TODO remove this ugliness... Qt is not good for this.

class ImageUpdater(QThread):
    update = Signal(QImage)

    def __init__(self, rtsp_url: str, parent=None):
        super().__init__(parent)
        self._max_fps = 60
        self._is_running = False
        self.capture = cv2.VideoCapture(
            f"rtspsrc location=\"{rtsp_url}\" ! rtph264depay ! h264parse ! avdec_h264 ! autovideoconvert ! appsink",
            cv2.CAP_GSTREAMER
        )

    def stop(self):
        self._is_running = False
        self.wait()

    def run(self):
        self.msleep(1000)
        self._is_running = True
        while self._is_running:
            result, frame = self.capture.read()
            if result:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                converted = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.update.emit(converted)
            self.msleep(int(1000 / self._max_fps))


class ImageWidget(QLabel):
    mouse_move = Signal(float, float)

    def __init__(self, loading_text: str, scale_factor=1.0, parent=None):
        super().__init__(loading_text, parent=parent)
        self.scale_factor = scale_factor

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_move.emit(event.x(), event.y())

    @Slot(QImage)
    def update_image(self, image: QImage):
        pix_map = QPixmap.fromImage(image)
        pix_map = pix_map.scaled(
            int(image.width() * self.scale_factor),
            int(image.height() * self.scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.setPixmap(pix_map)


class MainWindow(QMainWindow):
    def __init__(self, rtsp_url: str, parent=None):
        super().__init__(parent)
        self.image_updater = ImageUpdater(rtsp_url, self)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.position_label = QLabel("X: -, Y: -")
        self.status_bar.addWidget(self.position_label)

        self.central_widget = QWidget()

        self.main_grid = QGridLayout()
        self.secondary_grid = QGridLayout()
        self.main_grid.addLayout(self.secondary_grid, 0, 0)

        self.main_image = ImageWidget("Connecting...", 0.7)
        self.main_image.mouse_move.connect(lambda x, y: self.position_label.setText(f"X: {x}, Y: {y}"))
        self.main_grid.addWidget(self.main_image, 0, 1)

        self.roi_image = QLabel("No image data")
        self.secondary_grid.addWidget(self.roi_image, 0, 0)

        self.central_widget.setLayout(self.main_grid)
        self.setCentralWidget(self.central_widget)
        self.resize(1600, 800)
        self.setWindowTitle('Parking statistics')
        self.show()

        self.image_updater.update.connect(self.main_image.update_image, Qt.QueuedConnection)
        self.image_updater.start()

    def closeEvent(self, event: QCloseEvent):
        self.image_updater.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow("rtsp://admin:123@192.168.1.106:554/onvif1")
    sys.exit(app.exec_())
