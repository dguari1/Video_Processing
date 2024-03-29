import os
import sys
import cv2
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from multiprocessing import freeze_support

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from ImageViewerandProcess import ImageViewer

from queue import Queue
from threading import Thread
import time

"""
Created on 2019-06-27
@author: Diego L.Guarin -- Diego.Guarin@uhn.ca

This file will contain a new app for extracting movement features of videos using machine learning 

"""


class VideoHandler:
    
    def __init__(self, filename, queuesize = 30):
        
        self.video_filename = filename
        try:
            self.video_handler = cv2.VideoCapture(self.video_filename)
        except:
            # there was an error reading the file, return
            # we need to add error codes so that the user can knows what happened 
            return 

        self.video_length = int(self.video_handler.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(self.video_handler.get(cv2.CAP_PROP_FPS))
        self.playbackspeed = self.video_fps
        self.video_exist_landmarks = None
        self.video_landmarks_filename = None
        self.video_landmarks = None

        # the video loading will be performed in a different thread and then submitted to the main thread
        self.Q = Queue(maxsize=queuesize)
        self.Thread = Thread(target=self.update, args=())
        self.Thread.daemon = True
        self.stopped = False

    def start(self):
        #t = Thread(target=self.update, args=())
        #t.daemon = True
        #t.start()
        self.Thread.start()
        return self
        
    def update(self):
        # read the video stream and put them in the queue
        while True:
            
            if self.stopped:
                return 
            
            if not self.Q.full():
                
                grabbed, frame = self.video_handler.read()
                
                if not grabbed:
                    self.stop()
                    return
                
                self.Q.put(frame)
                
    def read(self):
        # return the next frame in the queue
        return self.Q.get()
    
    def more(self):
        # returns True if there are frames in the Queue 
        return self.Q.qsize() > 0
    
    def stop(self):
        # the thread should stop
        self.stopped = True



class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.video_length = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(self.stream.get(cv2.CAP_PROP_FPS))
        self.playbackspeed = self.video_fps
        self.stopped = False
        self.Thread = Thread(target=self.get, args=())
        
    def start(self):    
        self.Thread.start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
                return
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True
        
        
class VideoInformation:
    """
    Class that contains all the information related to the video. It provide a 
    read() function that passes frames from from a cv2.VideoCapture object
    """
    
    def __init__(self, filename):
        
        self.video_filename = filename
        try:
            self.video_handler = cv2.VideoCapture(self.video_filename)
        except:
            QtWidgets.QMessageBox.critical(0,"Error","Video file cannot be read");
            self.return_error()
            # there was an error reading the file, return
            # we need to add error codes so that the user can knows what happened

        self.video_length = int(self.video_handler.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(self.video_handler.get(cv2.CAP_PROP_FPS))
        self.playbackspeed = self.video_fps
        self.video_exist_landmarks = None
        self.video_landmarks_filename = None
        self.video_landmarks = None
        
        self.grabbed = False
        self.frame = None

    def read(self):
        # read frames
        (self.grabbed, self.frame) = self.video_handler.read()
        return self.grabbed, self.frame

    @staticmethod
    def return_error():
        return None


class UpdateSlider(QThread):
    """
        Class that will be used to update the video display according to the position of the
        slider. It uses a new thread to load the video frames
    """
    finished = pyqtSignal()
    frame_number = pyqtSignal(int)

    def __init__(self, video_handler=None, image_viewer=None):
        super(UpdateSlider, self).__init__()

        self.video_handler = video_handler
        self.image_viewer = image_viewer
        #self.slider_position = slider_value

    @pyqtSlot()
    def updateviewer(self, slider_value):
        self.video_handler.set(cv2.CAP_PROP_POS_FRAMES, slider_value)
        success, image = self.video_handler.read()
        if success:
            # update the view
            self.image_viewer._opencvimage = image
            self.image_viewer.update_view()
            # send back the frame number
            self.frame_number.emit(slider_value)
        else:
            # do not update the view, and send a None indicating an error
            self.frame_number.emit(None)

        print('que')
        # now inform that is over
        self.finished.emit()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # self.setGeometry(5,60,700,500)

        self.setWindowTitle('Video Processing')
        self.background_color = self.palette().color(QtGui.QPalette.Background)

        # if os.name is 'posix':  # is a mac or linux
        #     scriptDir = os.path.dirname(sys.argv[0])
        # else:  # is a  windows
        #     scriptDir = os.getcwd()

        # This is the main Window
        self.main_Widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_Widget)

        # Elements of the main window
        # image viewer
        self.displayImage = ImageViewer()

        # Menu bar __ Top - Main options
        self.menuBar = QtWidgets.QMenuBar(self)
        self.setStyleSheet("""
                                   QMenuBar {
                                   font-size:18px;
                                   background : transparent;
                                   }
                                   """)
        # Tool bar __ Top - Functions to analyze the current image
        self.toolBar_Top = QtWidgets.QToolBar(self)

        # Tool bar __ Bottom  - Play/pause buttons
        self.toolBar_Bottom = QtWidgets.QToolBar(self)

        # Frame Slider _ Bottom  - Easily move between frames
        self.slider_Bottom = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_Bottom.setMinimum(1)
        self.slider_Bottom.setMaximum(100)
        self.slider_Bottom.setValue(1)
        self.slider_Bottom.setTickInterval(1)
        self.slider_Bottom.setEnabled(False)
        self.slider_Bottom.valueChanged.connect(self.slidervaluechange)

        # Status Bar _ Bottom - Show the current frame number
        self.frameLabel = QtWidgets.QLabel('')
        self.frameLabel.setFont(QtGui.QFont("Times", 10))
        self.statusBar_Bottom = QtWidgets.QStatusBar()
        self.statusBar_Bottom.setFont(QtGui.QFont("Times", 10))
        self.statusBar_Bottom.addPermanentWidget(self.frameLabel)

        # Definition of Variables
        self.video_handler = None
        self.video_name = None  # name and location of video file
        self.current_frame = 0  # what is the current frame
        self.timer = QtCore.QTimer()  # controls video playback

        # threads used to process data and help in the visualization
        self.thread_slider = QThread() # no parent
        self.class_slider = UpdateSlider()

        # initialize the User Interface
        self.initUI()
        self.show()

    def initUI(self):

        # Populate the different menus
        file_menu = self.menuBar.addMenu("&File")

        load_video = file_menu.addAction("Load Video File")
        load_video.setShortcut("Ctrl+F")
        load_video.setStatusTip('Load video file, accepted formats : .mp4, .avi, .mov')
        load_video.triggered.connect(self.openvideofile)

        load_landmarks = file_menu.addAction("Load Landmarks File")
        load_landmarks.setShortcut("Ctrl+L")
        load_landmarks.setStatusTip('Load landmark file, accepted formats : .csv')
        # load_landmarks.triggered.connect(self.load_file)

        quit_program = file_menu.addAction("Quit")
        quit_program.setShortcut("Ctrl+Q")
        # quit_program.triggered.connect(self.load_file)

        video_menu = self.menuBar.addMenu("&Video")
        play_video = video_menu.addAction("Play Video")
        play_video.setShortcut("Ctrl+P")
        play_video.setStatusTip('Play video at given playback speed')
        # play_video.triggered.connect(self.load_file)

        stop_video = video_menu.addAction("Stop Video")
        stop_video.setShortcut("Ctrl+S")
        stop_video.setStatusTip('Stop video playback')
        # stop_video.triggered.connect(self.load_file)

        jump_to_frame = video_menu.addAction("Jump to Frame")
        jump_to_frame.setShortcut("Ctrl+J")
        jump_to_frame.setStatusTip('Jump to certain frame')
        # jump_to_frame.triggered.connect(self.load_file)

        playback_settings = video_menu.addAction("Playback Settings")
        playback_settings.setShortcut("Ctrl+P")
        playback_settings.setStatusTip('Define video playback settings')
        # playback_settings.triggered.connect(self.load_file)

        landmarks_menu = self.menuBar.addMenu("&Landmarks")
        # process_current_frame = landmarks_menu.addAction("Process Current Frame")
        # process_current_frame.setShortcut("Ctrl+C")
        # process_current_frame.setStatusTip('Determine facial landmarks for current frame')
        # # process_current_frame.triggered.connect(self.load_file)

        process_some_frame = landmarks_menu.addAction("Process Frames")
        process_some_frame.setShortcut("Ctrl+S")
        process_some_frame.setStatusTip('Determine facial landmarks for some frames in the video')
        # process_some_frame.triggered.connect(self.load_file)

        process_all_frame = landmarks_menu.addAction("Process All Frames")
        process_all_frame.setShortcut("Ctrl+A")
        process_all_frame.setStatusTip('Determine facial landmarks for all frames in the video')
        # process_all_frame.triggered.connect(self.load_file)

        process_settings = landmarks_menu.addAction("Process Frames Settings")
        process_settings.setShortcut("Ctrl+L")
        process_settings.setStatusTip('Determine facial landmarks for all frames in the video')
        # process_settings.triggered.connect(self.load_file)

        # fill the top toolbar

        process_current_frame =  QtWidgets.QAction('Process current frame', self)
        process_current_frame.setIcon(QtGui.QIcon('./icons/facial-analysis.png'))
        # process_current_frame.connect(self.match_iris)

        toggle_landmark = QtWidgets.QAction('Show/Hide facial landmarks', self)
        toggle_landmark.setIcon(QtGui.QIcon('./icons/facial-analysis.png'))
        # toggle_landmark.connect(self.match_iris)

        manual_adjustment = QtWidgets.QAction('Manually adjust landmarks position in current frame', self)
        manual_adjustment.setIcon(QtGui.QIcon('./icons/facial-analysis.png'))
        # manual_adjustment.connect(self.match_iris)

        landmark_settings = QtWidgets.QAction('Adjust landmark visualization settings', self)
        landmark_settings.setIcon(QtGui.QIcon('./icons/facial-analysis.png'))
        # landmark_settings.connect(self.match_iris)

        show_metrics = QtWidgets.QAction('Display facial metrics in current frame', self)
        show_metrics.setIcon(QtGui.QIcon('./icons/facial-metrics.png'))
        # show_metrics.connect(self.match_iris)

        snapshot = QtWidgets.QAction('Save snapshot of current view', self)
        snapshot.setIcon(QtGui.QIcon('./icons/profile.png'))
        # snapshot.connect(self.match_iris)

        self.toolBar_Top.addActions((process_current_frame, toggle_landmark, manual_adjustment, landmark_settings, show_metrics, snapshot))
        self.toolBar_Top.setIconSize(QtCore.QSize(50, 50))
        for action in self.toolBar_Top.actions():
            widget = self.toolBar_Top.widgetForAction(action)
            widget.setFixedSize(50, 50)

        self.toolBar_Top.setMinimumSize(self.toolBar_Top.sizeHint())
        self.toolBar_Top.setStyleSheet('QToolBar{spacing:8px;}')

        # fill the bottom toolbar
        play_action = QtWidgets.QAction('Play', self)
        play_action.setShortcut('Shift+S')
        play_action.setIcon(QtGui.QIcon('./icons/play-arrow.png'))
        play_action.triggered.connect(self.playvideo)

        stop_action = QtWidgets.QAction('Stop', self)
        stop_action.setShortcut('Shift+Z')
        stop_action.setIcon(QtGui.QIcon('./icons/pause.png'))
        stop_action.triggered.connect(self.stopvideo)

        fastforward_action = QtWidgets.QAction('Fast Forward', self)
        fastforward_action.setShortcut('Shift+D')
        fastforward_action.setIcon(QtGui.QIcon('./icons/fast-forward.png'))
        # fastforward_action.triggered.connect(self.match_iris)

        rewind_action = QtWidgets.QAction('Rewind', self)
        rewind_action.setShortcut('Shift+A')
        rewind_action.setIcon(QtGui.QIcon('./icons/rewind.png'))
        # rewind_action.triggered.connect(self.match_iris)

        # spacer widget for left
        left_spacer = QtWidgets.QWidget(self)
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # spacer widget for right
        right_spacer = QtWidgets.QWidget(self)
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # fill the bottom toolbar
        self.toolBar_Bottom.addWidget(left_spacer)
        self.toolBar_Bottom.addActions((rewind_action, play_action, stop_action, fastforward_action))
        self.toolBar_Bottom.addWidget(right_spacer)
        self.toolBar_Bottom.setIconSize(QtCore.QSize(35, 35))
        # for action in self.toolBar_Bottom.actions():
        #     widget = self.toolBar_Bottom.widgetForAction(action)
        #     widget.setFixedSize(35, 35)

        self.toolBar_Bottom.setMinimumSize(self.toolBar_Bottom.sizeHint())
        self.toolBar_Bottom.setStyleSheet('QToolBar{spacing:8px;}')

        # Create the layout

        # The main window has 6 components in the following order:
        # Menu Bar - Tool Bar - Image viewer - Tool Bar - Slider - Status Bar

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.menuBar)
        layout.addWidget(self.toolBar_Top)
        layout.addWidget(self.displayImage)
        layout.addWidget(self.toolBar_Bottom)
        layout.addWidget(self.slider_Bottom)
        self.setStatusBar(self.statusBar_Bottom)

        # Set the defined layout in the main window
        self.main_Widget.setLayout(layout)
        
        self.setGeometry(300, 100, 600, 800)

    def openvideofile(self):
        # load a file using the widget
        name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Load Video File',
            '', "Video files (*.mp4 *.avi *.mov *.MP4 *.AVI *.MOV)")

        if not name:
            pass
        else:

            name = os.path.normpath(name)
            # Remove previous video handlers to avoid taking odd frames
            self.video_handler = None
            # change window name to match the file name
            self.setWindowTitle('Video Processing - ' + name.split(os.path.sep)[-1])

            # user provided a video, open it using OpenCV
            self.video_handler = VideoInformation(name)  # read the video
            success, image = self.video_handler.read()  # get the first frame

            # video was read sucessfully, update this information in the class taking care of the slider
            self.class_slider.video_handler = self.video_handler.video_handler
            self.class_slider.image_viewer = self.displayImage
            
            if success:  # if the frame exists then show the image
                self.displayImage._opencvimage = image             
                self.displayImage.update_view()
                self.current_frame = 0
                # put the frame information in the app
                self.frameLabel.setText('Frame :'+str(int(self.current_frame)+1)+'/'+str(self.video_handler.video_length))
                # update the slider
                self.slider_Bottom.setMinimum(1)
                self.slider_Bottom.setMaximum(self.video_handler.video_length)
                self.slider_Bottom.blockSignals(True)
                self.slider_Bottom.setValue(1)
                self.slider_Bottom.blockSignals(False)
                self.slider_Bottom.setEnabled(True)
            # videocap.release()

    def playvideo(self):
        # verify that the video handler is not empty
        if self.video_handler is not None:
        
            self.timer.timeout.connect(self.nextframefunction)
            self.timer.start(1000.0/self.video_handler.playbackspeed)

    def nextframefunction(self):
        # verify that we are not at the last frame
        if self.current_frame < self.video_handler.video_length - 1:
            success, image = self.video_handler.read()  # get the first frame
            self.displayImage._opencvimage = image
            self.displayImage.update_view()
            self.current_frame += 1
            # put the frame information in the app
            self.frameLabel.setText(
                'Frame :' + str(int(self.current_frame) + 1) + '/' + str(self.video_handler.video_length))
            # update the slider
            self.slider_Bottom.blockSignals(True)
            self.slider_Bottom.setValue(self.current_frame + 1)
            self.slider_Bottom.blockSignals(False)

        else:
            # reached the end of the video
            self.timer.stop()

    def stopvideo(self):
        # stop video if video is playing
        if self.timer.isActive():  # verify is the video is running
            self.timer.stop()

    def slidervaluechange(self):
        """
        this functions read the slider, updates the view and then updates the slider according
        to the frame that is being displayed. Everything occurs in a new thread, so it is usually
        is slow as firing up and endings threads takes time. However, this is the best solution to
        prevent the UI from frozen, as the process of reading 'certain' frames from a cv2 video object
        is very slow and blocking
        """
        if self.timer.isActive():  # verify is the video is running
            # top video playback before moving slider
            self.timer.stop()

        # read slider value from slider
        slider_value = self.slider_Bottom.value()
        # move the class that updates the viewer and slider to a new thread
        self.class_slider.moveToThread(self.thread_slider)
        # star the thread
        self.thread_slider.start()
        # update the view, pass the slider position to the function
        self.thread_slider.started.connect(lambda: self.class_slider.updateviewer(slider_value))
        # if the view was successfully updated, update the slider position
        self.class_slider.frame_number.connect(self.updateviwefromslider)
        # end the thread
        self.class_slider.finished.connect(self.thread_slider.quit)

    @pyqtSlot(int)
    def updateviwefromslider(self, frame_number):
        if frame_number is not None:
            self.current_frame = frame_number - 1
            self.frameLabel.setText(
                'Frame : ' + str(int(self.current_frame) + 1) + '/' + str(self.video_handler.video_length))
            #self.slider_Bottom.blockSignals(True)
            self.slider_Bottom.setValue(int(self.current_frame) + 1)
            #self.slider_Bottom.blockSignals(False)



if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    freeze_support()

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

    GUI = MainWindow()
    GUI.show()
    app.exec_()