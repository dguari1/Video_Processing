from PyQt5.QtCore import QDir, QSize, QSizeF, Qt, QUrl
from PyQt5.QtGui import QTransform
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QApplication, QFileDialog, QGraphicsScene,
        QGraphicsView, QHBoxLayout, QPushButton, QSlider, QStyle, QVBoxLayout,
        QWidget)


class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setSize(QSizeF(640, 480))

        scene = QGraphicsScene(self)
        graphicsView = QGraphicsView(scene)

        scene.addItem(self.videoItem)

        rotateSlider = QSlider(Qt.Horizontal)
        rotateSlider.setRange(-180,  180)
        rotateSlider.setValue(0)
        rotateSlider.valueChanged.connect(self.rotateVideo)

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(graphicsView)
        layout.addWidget(rotateSlider)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoItem)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def sizeHint(self):
        return QSize(800, 600)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def rotateVideo(self, angle):
        x = self.videoItem.boundingRect().width() / 2.0
        y = self.videoItem.boundingRect().height() / 2.0

        self.videoItem.setTransform(
                QTransform().translate(x, y).rotate(angle).translate(-x, -y))


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    player = VideoPlayer()
    player.show()

    sys.exit(app.exec_())