# -*- coding: utf-8 -*-
"""
Created on 2019-06-27
@author: Diego L.Guarin -- Diego.Guarin@uhn.ca
"""
import os
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtCore import QFile, QTextStream

"""

"""


class ProcessingWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ProcessingWindow, self).__init__(parent)
        
        self.setWindowTitle('Processing Frames')

        #self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'ruler_icon.ico'))


        self.numberoflistboundingbox = 1 #this variable counts the number of list used to crete the frames in the bounding box 

        # initialize the User Interface
        self.initUI()
        self.show()

    def initUI(self):

        newfont = QtGui.QFont("Times", 12)

        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(10, 0)

        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0, 10)

        boundingbox = QtWidgets.QGroupBox('')
        boundingbox.setStyleSheet(self.getStyleSheet('./include/GroupBoxStyle.qss'))
        self.boundingboxLayout = QtWidgets.QGridLayout()
        #RestLayout.addWidget(self.Rest, 0, 0, 1, 1)
        boundingbox.setLayout(self.boundingboxLayout)

        processframes = QtWidgets.QGroupBox('Process Frames')
        processframes.setStyleSheet(self.getStyleSheet('./include/GroupBoxStyle.qss'))
        processframesLayout = QtWidgets.QGridLayout()
        # RestLayout.addWidget(self.Rest, 0, 0, 1, 1)
        processframes.setLayout(processframesLayout)

        # # help buttons
        # self._help_CE = QtWidgets.QPushButton('', self)
        # self._help_CE.setIcon(QtGui.QIcon(
        #     scriptDir + os.path.sep + 'include' + os.path.sep + 'icon_color' + os.path.sep + 'question_icon.png'))
        # pixmap_CE = QtGui.QPixmap.fromImage(QtGui.QImage(
        #     scriptDir + os.path.sep + 'include' + os.path.sep + 'measures' + os.path.sep + 'commissure_excursion.png'))
        # text_CE_title = 'Commissure Excursion:'
        # text_CE_content = 'Distance from midline vertical / lower lip vermillion junction point to the oral commissure'
        # self._help_CE.clicked.connect(lambda: self.push_help_CE(pixmap_CE, text_CE_title, text_CE_content))
        # self._help_CE.setIconSize(QtCore.QSize(20, 20))
        
        addbutton = QtWidgets.QPushButton('Push')
        addbutton.clicked.connect(self.addNewRow)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(spacerv, 0, 0)
        layout.addWidget(boundingbox, 1, 0, 1, 1)
        layout.addWidget(spacerv, 2, 0)
        layout.addWidget(processframes, 3, 0, 1, 1)
        layout.addWidget(spacerh, 4, 0)
        layout.addWidget(addbutton, 5, 0, 1, 1)
        # layout.addWidget(spacerh, 0, 7)
        # layout.addWidget(self._label0d, 0, 8, 1, 1)


        label_allframes = QtWidgets.QLabel('All Frames')
        label_allframes.setFont(newfont)
        label_allframes.setFixedWidth(100)

        label_firstframes = QtWidgets.QLabel('First Frame')
        label_firstframes.setFont(newfont)
        label_firstframes.setFixedWidth(100)

        label_frames1 = QtWidgets.QLabel('Frames')
        label_frames1.setFont(newfont)
        label_frames1.setFixedWidth(100)
        
        label_frames2 = QtWidgets.QLabel('Frames')
        label_frames2.setFont(newfont)
        label_frames2.setFixedWidth(100)
        
        label_init = QtWidgets.QLabel('init')
        label_init.setFont(QtGui.QFont("Times", 10))
        label_init.setMinimumWidth(25)
        label_init.setAlignment(QtCore.Qt.AlignCenter)
        
        label_step = QtWidgets.QLabel('step')
        label_step.setFont(QtGui.QFont("Times", 10))
        label_step.setMinimumWidth(25)
        label_step.setAlignment(QtCore.Qt.AlignCenter)
        
        label_end = QtWidgets.QLabel('end')
        label_end.setFont(QtGui.QFont("Times", 10))
        label_end.setMinimumWidth(25)
        label_end.setAlignment(QtCore.Qt.AlignCenter)
        
        label_empty = QtWidgets.QLabel('')
        label_empty.setFont(QtGui.QFont("Times", 10))
        label_empty.setFixedWidth(25)
        label_empty.setFixedHeight(25)
        label_empty.setAlignment(QtCore.Qt.AlignCenter)
        
        layoutadditionalframes_labels = QtWidgets.QHBoxLayout()
        layoutadditionalframes_labels.addWidget(label_init, QtCore.Qt.AlignCenter)
        layoutadditionalframes_labels.addWidget(label_step, QtCore.Qt.AlignCenter)
        layoutadditionalframes_labels.addWidget(label_end, QtCore.Qt.AlignCenter)
        layoutadditionalframes_labels.addWidget(label_empty)
        

        self.allframestick_boundingbox = QtWidgets.QCheckBox('')
        self.allframestick_boundingbox.setChecked(False)
        self.allframestick_boundingbox.setFixedWidth(25)

        self.firstframetick_boundingbox = QtWidgets.QCheckBox('')
        self.firstframetick_boundingbox.setChecked(False)
        self.firstframetick_boundingbox.setFixedWidth(25)

        self.framelistboundingbox = QtWidgets.QLineEdit()
        #self.framelistboundingbox.setFixedWidth(100)
        self.framelistboundingbox.setMinimumWidth(75)
        self.framelistboundingbox.setFixedHeight(25)
        self.framelistboundingbox.setFont(QtGui.QFont("Times", 8))

        self.framelistboundingbox.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^(\d+(,\d+)*)?$")))
        
        RegExpVal = QtGui.QRegExpValidator(QtCore.QRegExp("^(\d+)?$"))
        
        self.frameinitboundingbox_1 = QtWidgets.QLineEdit()
        self.frameinitboundingbox_1.setMinimumWidth(50)
        self.frameinitboundingbox_1.setFixedHeight(25)
        self.frameinitboundingbox_1.setFont(QtGui.QFont("Times", 8))
        self.frameinitboundingbox_1.setValidator(RegExpVal)
        self.frameinitboundingbox_1.setAlignment(QtCore.Qt.AlignCenter)
        
        self.framestepboundingbox_1 = QtWidgets.QLineEdit()
        self.framestepboundingbox_1.setMinimumWidth(50)
        self.framestepboundingbox_1.setFixedHeight(25)
        self.framestepboundingbox_1.setFont(QtGui.QFont("Times", 8))
        self.framestepboundingbox_1.setValidator(RegExpVal)
        self.framestepboundingbox_1.setAlignment(QtCore.Qt.AlignCenter)
        
        self.frameendboundingbox_1 = QtWidgets.QLineEdit()
        self.frameendboundingbox_1.setMinimumWidth(50)
        self.frameendboundingbox_1.setFixedHeight(25)
        self.frameendboundingbox_1.setFont(QtGui.QFont("Times", 8))
        self.frameendboundingbox_1.setValidator(RegExpVal)
        self.frameendboundingbox_1.setAlignment(QtCore.Qt.AlignCenter)
        
        self.buttontoaddlines = QtWidgets.QPushButton('')
        self.buttontoaddlines.setIcon(QtGui.QIcon('./icons/plus.png'))
        self.buttontoaddlines.setIconSize(QtCore.QSize(25,25))
        
        
        
        layoutadditionalframes_lines = QtWidgets.QHBoxLayout()
        layoutadditionalframes_lines.addWidget(self.frameinitboundingbox_1)
        layoutadditionalframes_lines.addWidget(self.framestepboundingbox_1)
        layoutadditionalframes_lines.addWidget(self.frameendboundingbox_1)
        layoutadditionalframes_lines.addWidget(self.buttontoaddlines)
        

        self.boundingboxLayout.addWidget(label_allframes, 0, 0, 1, 1)
        self.boundingboxLayout.addWidget(self.allframestick_boundingbox, 0, 1, 1, 1)
        self.boundingboxLayout.addWidget(label_firstframes, 1, 0, 1, 1)
        self.boundingboxLayout.addWidget(self.firstframetick_boundingbox, 1, 1, 1, 1)
        self.boundingboxLayout.addWidget(label_frames1, 2, 0, 1, 1)
        self.boundingboxLayout.addWidget(self.framelistboundingbox, 2, 1, 1, 1)
        
        self.boundingboxLayout.addLayout(layoutadditionalframes_labels, 3, 1, 1, 1)
        self.boundingboxLayout.addWidget(label_frames2, 4, 0, 1, 1)
        self.boundingboxLayout.addLayout(layoutadditionalframes_lines, 4, 1, 1, 1)


        self.setLayout(layout)


    def addNewRow(self):
        self.pushButton = QtWidgets.QPushButton('I am in Test widget')
        self.boundingboxLayout.addWidget(Test(widget = self.pushButton))


    # this function read the style sheet used to presents the GroupBox,
    # it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
            f = QFile(path)
            f.open(QFile.ReadOnly | QFile.Text)
            stylesheet = QTextStream(f).readAll()
            f.close()
            return stylesheet

    def push_help_CE(self, text_title='', text_content=''):
        pass
    


class Test(QtWidgets.QWidget):
  def __init__( self, widget, parent=None):
      super(Test, self).__init__(parent)

      #self.pushButton = QtWidgets.QPushButton('I am in Test widget')

      layout = QtWidgets.QHBoxLayout()
      layout.addWidget(widget)
      self.setLayout(layout)
      
      #return self

        
if __name__ == '__main__':
#    app = QtWidgets.QApplication([])
#    GUI = ProcessingWindow()
#    GUI.show()
#    app.exec_()
#
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

    GUI = ProcessingWindow()
    GUI.show()
    app.exec_()
    