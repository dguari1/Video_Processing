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
    def __init__(self):
        super(ProcessingWindow, self).__init__()
        
        self.setWindowTitle('Processing Frames')

        #self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'ruler_icon.ico'))


        # initialize the User Interface
        self.initUI()
        self.show()

    def initUI(self):
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(10, 0)

        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0, 10)

        boundingbox = QtWidgets.QGroupBox('Bounding Box')
        boundingbox.setStyleSheet(self.getStyleSheet('./include/GroupBoxStyle.qss'))
        boundingboxLayout = QtWidgets.QGridLayout()
        #RestLayout.addWidget(self.Rest, 0, 0, 1, 1)
        boundingbox.setLayout(boundingboxLayout)

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

        layout = QtWidgets.QGridLayout()
        layout.addWidget(spacerv, 0, 0)
        layout.addWidget(boundingbox, 1, 0, 1, 1)
        layout.addWidget(spacerv, 2, 0)
        layout.addWidget(processframes, 3, 0, 1, 1)
        layout.addWidget(spacerh, 4, 0)
        # layout.addWidget(self._label0c, 0, 6, 1, 1)
        # layout.addWidget(spacerh, 0, 7)
        # layout.addWidget(self._label0d, 0, 8, 1, 1)

        self.setLayout(layout)

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

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    GUI = ProcessingWindow()
    GUI.show()
    app.exec_()
    