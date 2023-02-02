#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from typing import Any

import mediapipe as mp
import numpy as np
from PySide6 import QtCore
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import (QCamera, QCameraDevice, QImageCapture,
                                  QMediaCaptureSession, QMediaDevices,
                                  QMediaRecorder)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout,
                               QWidget)

Pose = mp.solutions.pose.Pose


class MainWindow(QWidget):
    def __init__(self, device: QCameraDevice):
        super().__init__()  # TODO Set title
        # Detector
        # self.pose = Pose(static_image_mode=False,
        #                  model_complexity=1)
        # Layout
        self.video = QVideoWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.video)
        # Camera settings
        self.camera = QCamera(device)
        # self.capture = QImageCapture(self.camera)
        self.recorder = QMediaRecorder()
        self.session = QMediaCaptureSession()
        self.session.setCamera(self.camera)
        # self.session.setImageCapture(self.capture)
        self.session.setRecorder(self.recorder)
        self.session.setVideoOutput(self.video)
        self.camera.start()
        self.recorder.record()

    def closeEvent(self, event) -> bool:
        if self.camera.isActive():
            self.camera.stop()
        event.accept()

    @QtCore.Slot(int, QImage)
    def frameRead(self, id: int, preview: QImage) -> None:
        print(np.frombuffer(preview.bits(), np.uint8).reshape((
            preview.height(), preview.width(), 3)))


if __name__ == '__main__':
    parser = ArgumentParser()
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument(
        '-l', '--list', action='store_true',
        help='List available video input devices.')
    options.add_argument(
        '-i', '--input-id', type=int,
        help='Select input video device by its id. Execute -l ' +
        'to show available resources.')
    args = parser.parse_args()

    if args.list:
        for i, dev in enumerate(QMediaDevices.videoInputs()):
            print(
                f'Id: {i}\tName: {dev.description()} ({dev.photoResolutions()})')
        sys.exit(0)

    app = QApplication([])
    window = MainWindow(QMediaDevices.videoInputs()[args.input_id])
    window.showMaximized()
    sys.exit(app.exec())
