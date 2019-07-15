# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:53:19 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import cv2
import numpy as np
from scipy.spatial.distance import cdist

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


from utilities import mark_picture  #this function draws the landmarks and iris circles 
from process_eye import get_iris_manual #this function opens a new window to manually select the iris


"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ImageViewer(QtWidgets.QGraphicsView):       
    
    def __init__(self):
        # usual parameters to make sure the image can be zoom-in and out and is
        # possible to move around the zoomed-in view
        super(ImageViewer, self).__init__()
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(100,100,100)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        
        # this is used to show the dots and update the dots in image
        self._shape = None
        self._lefteye = None
        self._righteye = None
        self._opencvimage = None
        self._boundingbox = None
        self._PointToModify = None
        self._points = None
        self._landmark_size = None
        self._store_old_value = None

        # this variable is used to verify is a landmark will be relocated
        self._IsPointLifted = False
        
        # this variable is used to verify if the user wants to drag the eyes to a different location
        self._IsDragEyes = False
        # and what eye is the person trying to move
        self._IsDragLeft = False
        self._IsDragRight = False
        self._BothEyesTogether = False

    def setPhoto(self, pixmap = None):
        # this function puts an image in the scece (if pixmap is not None), it
        # sets the zoom to zero
        self._zoom = 0        
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def fitInView(self):
        # this function takes care of accommodating the view so that it can fit
        # in the scene, it resets the zoom to 0 (i think is a overkill, i took
        # it from somewhere else)
        rect = QtCore.QRectF(self._photo.pixmap().rect())

        if not rect.isNull():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())        
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
            self.scale(factor, factor)
            self.centerOn(rect.center())
            self._zoom = 0                        
            
    def zoomFactor(self):
        return self._zoom
    
    def wheelEvent(self, event):
        # this take care of the zoom, it modifies the zoom factor if the mouse
        # wheel is moved forward or backward by 20%
        if not self._photo.pixmap().isNull():
            move=(event.angleDelta().y()/120)
            if move > 0:
                factor = 1.2
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
                                        
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom <= 0:
                self._zoom = 0
                self.fitInView()

    def mousePressEvent(self, event):

        # this function takes care of lifting (if RightClick) and relocating (if
        # a point is lifted and LeftClick) landmarks.

        if not self._photo.pixmap().isNull():
            scenePos = self.mapToScene(event.pos())
            if event.button() == QtCore.Qt.RightButton:
                # if the user RightClick and no point is lifted then verify if
                # the position of the click is close to one of the landmarks
                if self._IsPointLifted is False:
                    if self._shape is not None:
    
                        x_mousePos = scenePos.toPoint().x()
                        y_mousePos = scenePos.toPoint().y()
                        mousePos = np.array([(x_mousePos, y_mousePos)])
                        distance = cdist(self._shape, mousePos)
                        distance = distance[:, 0]
                        # check if a landmark (including the eyes) is no more than
                        # 3 pixels away from the click location. If there is then lift that
                        # landmark from the face. If the image is taller than 1000 pixels
                        # then the distance is 6 pixels
                        if self._scene.height() < 1000:                           
                            PointToModify = [i for i, j in enumerate(distance) if j <= 3]
                        else:
                            PointToModify = [i for i, j in enumerate(distance) if j <= 6]

                        if PointToModify:
                            self._PointToModify = PointToModify[0]
                            self._store_old_value = self._shape[self._PointToModify].copy()
                            self._shape[self._PointToModify] = [-1, -1]
                            self._IsPointLifted = True
                            self.set_update_photo()

            elif event.button() == QtCore.Qt.LeftButton:
                # if the user LeftClick and there is a landmark lifted, then
                # reposition the landmark in the position of the click
                if self._IsPointLifted:
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()
                    self._shape[self._PointToModify] = [x_mousePos, y_mousePos]
                    self._IsPointLifted = False
                    self._PointToModify = None
                    self.set_update_photo()

                else:
                    # The user is probably going to pan around, allow this
                    self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                            
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
            
    # def mouseReleaseEvent(self, event):
    #     # this function defines what happens when you release the mouse click
    #
    #     if not self._BothEyesTogether: #the user moved a single eye. This will only happen if the click is not realease
    #         #remove the Drag option
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #         #return the cursor to an arrow (in case that it was changes to a cross)
    #         self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
    #         #remove the option to drag the eyes (if click was released then draggin is over)
    #         self._IsDragEyes = False
    #         self._IsDragLeft = False
    #         self._IsDragRight = False
    #         self._BothEyesTogether = False
    #         self.set_update_photo()
    #         #update the viewer to present the latest postion of landmarks and iris
    #     elif self._BothEyesTogether: #the user is moving both eyes together. The eyes will be moved until a new click is pressed
    #         #remove the Drag option
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #
    #     QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

   
    # def mouseDoubleClickEvent(self, event):
    #
    #     #if the user double click on one of the iris the both iris will be able to move together
    #     if event.button() == QtCore.Qt.LeftButton:
    #         event.accept()
    #         if self._shape is not None:
    #             scenePos = self.mapToScene(event.pos())
    #             x_mousePos = scenePos.toPoint().x()
    #             y_mousePos = scenePos.toPoint().y()
    #             mousePos=np.array([(x_mousePos, y_mousePos)])
    #             distance=cdist([[self._righteye[0],self._righteye[1]],
    #                             [self._lefteye[0],self._lefteye[1]]]
    #                             , mousePos)
    #             distance=distance[:,0]
    #             #check if a landmark (including the eyes) is no more than
    #             #3 pixels away from the click location. If there is then lift that
    #             #landmark from the face. If the image is taller than 1000 pixels
    #             #then the distance is 5 pixels
    #             if self._scene.height() < 1000:
    #                 PointToModify = [i for i, j in enumerate(distance) if j <=3 ]
    #             else:
    #                 PointToModify = [i for i, j in enumerate(distance) if j <=6 ]
    #
    #             if PointToModify:
    #                 self._PointToModify = PointToModify[0]
    #                 if self._PointToModify == 0:
    #                     #user wants to move the right eye, Both eyes have to move together
    #                     self._IsDragEyes = True
    #                     self._IsDragRight = True
    #                     self._IsDragLeft = False
    #                     self._BothEyesTogether = True
    #
    #                 elif self._PointToModify == 1:
    #                     #user wants to move the left eye, Both eyes have to move together
    #                     self._IsDragEyes = True
    #                     self._IsDragRight = False
    #                     self._IsDragLeft = True
    #                     self._BothEyesTogether = True
    #
    #
    #                 #remove the iris from the image
    #                 self.set_update_photo()
    #                 #remove the Drag option
    #                 self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #                 #make the cursor a cross to facilitate localization of eye center
    #                 self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    #
    #
    #     else:
    #         event.ignore()
    #
    #     self.draw_circle(self._righteye)
    #     self.draw_circle(self._lefteye)
    #     QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)

    # def mouseMoveEvent(self, event):
    #     # this function takes care of the pan (move around the photo)
    #
    #     #if _IsDragEyes == true then the user wants to change the position of the eyes
    #     if self._IsDragEyes is True and self._BothEyesTogether is False:
    #         event.accept()
    #         for item in self._scene.items():
    #             if isinstance(item, QtWidgets.QGraphicsEllipseItem):
    #                 self._scene.removeItem(item)
    #
    #         scenePos = self.mapToScene(event.pos())
    #         x_mousePos = scenePos.toPoint().x()
    #         y_mousePos = scenePos.toPoint().y()
    #
    #         if self._IsDragLeft: #the user wants to move the left eye
    #             #update the position of the left eye with the current mouse position
    #             self._lefteye = [x_mousePos, y_mousePos, self._lefteye[2]]
    #             #draw a circle
    #             self.draw_circle(self._lefteye)
    #
    #
    #         elif self._IsDragRight:
    #             #update the position of the right eye with the current mouse position
    #             self._righteye = [x_mousePos, y_mousePos, self._righteye[2]]
    #             #draw a circle
    #             self.draw_circle(self._righteye)
    #
    #     elif self._IsDragEyes is True and self._BothEyesTogether is True:
    #         event.accept()
    #         for item in self._scene.items():
    #             if isinstance(item, QtWidgets.QGraphicsEllipseItem):
    #                 self._scene.removeItem(item)
    #
    #         scenePos = self.mapToScene(event.pos())
    #         x_mousePos = scenePos.toPoint().x()
    #         y_mousePos = scenePos.toPoint().y()
    #
    #         if self._IsDragLeft: #the user wants to move the left eye
    #             #update the position of the left eye with the current mouse position
    #             delta_x = x_mousePos-self._lefteye[0]
    #             delta_y = y_mousePos-self._lefteye[1]
    #             self._lefteye = [x_mousePos, y_mousePos, self._lefteye[2]]
    #             self._righteye = [self._righteye[0]+delta_x, self._righteye[1]+delta_y, self._righteye[2]]
    #
    #             #draw a circle
    #             self.draw_circle(self._lefteye)
    #             self.draw_circle(self._righteye)
    #
    #         if self._IsDragRight: #the user wants to move the right eye
    #             #update the position of the right eye with the current mouse position
    #             delta_x = x_mousePos-self._righteye[0]
    #             delta_y = y_mousePos-self._righteye[1]
    #             self._righteye = [x_mousePos, y_mousePos, self._righteye[2]]
    #             self._lefteye = [self._lefteye[0]+delta_x, self._lefteye[1]+delta_y, self._lefteye[2]]
    #
    #             #draw a circle
    #             self.draw_circle(self._righteye)
    #             self.draw_circle(self._lefteye)
    #
    #     else:
    #         event.ignore()
    #
    #     QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    # def draw_circle(self, CircleInformation ):
    #     #this function draws an circle with specific center and radius
    #
    #     Ellipse = QtWidgets.QGraphicsEllipseItem(0,0,CircleInformation[2]*2,CircleInformation[2]*2)
    #     #ellipse will be green
    #     pen = QtGui.QPen(QtCore.Qt.green)
    #     #set the ellipse line width according to the image size
    #     if self._scene.height() < 1000:
    #         pen.setWidth(1)
    #     else:
    #         pen.setWidth(3)
    #
    #     Ellipse.setPen(pen)
    #     #if I want to fill the ellipse i should do this:
    #     #brush = QtGui.QBrush(QtCore.Qt.green)
    #     #Ellipse.setPen(brush)
    #
    #     #this is the position of the top-left corner of the ellipse.......
    #     Ellipse.setPos(CircleInformation[0]-CircleInformation[2],CircleInformation[1]-CircleInformation[2])
    #     Ellipse.setTransform(QtGui.QTransform())
    #     self._scene.addItem(Ellipse)


    def set_update_photo(self, toggle=True):

        # this function takes care of updating the view without re-setting the
        # zoom. Is useful for when you lift or relocate landmarks or when
        # drawing lines in the middle of the face
        if self._opencvimage is not None:
            self._scene.removeItem(self._photo)
            
            temp_image = self._opencvimage.copy()
            
            if toggle:  # verify if the user wants to remove the landmarks..
                # if shape then draw 68 landmark points
                if self._shape is not None:
                    # mark_picture takes care of drawing the landmarks and the circles
                    # in the iris using opencv
                    temp_image = mark_picture(temp_image, self._shape, self._points, self._landmark_size)

            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            
            self._photo.setPixmap(img_show)    
            self._scene.addItem(self._photo)
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def show_entire_image(self):
        # this is a little utility to reset the zoom with a single click
        self.fitInView()

    def resizeEvent(self, event):
        # this function assure that when the main window is resized the image
        # is also resized preserving the h/w ratio
        self.fitInView()

    def update_view(self):
        # this function takes care of updating the view by re-setting the zoom.
        # is useful to place the image in the scene for the first time

        # if shape then add shape to image
        if self._opencvimage is not None:
            temp_image = self._opencvimage.copy()
        
            # draw 68 landmark points
            if self._shape is not None:
                temp_image = mark_picture(temp_image, self._shape, self._points, self._landmark_size)
    
            image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            
            # show the photo
            self.setPhoto(img_show)

    def keyPressEvent(self, event):
        # this function handles the Undo functionality
        modifiers = event.modifiers()
        key_pressed = event.key()
        if (modifiers & QtCore.Qt.ControlModifier) and (key_pressed == QtCore.Qt.Key_Z):
            if self._IsPointLifted:
                self._shape[self._PointToModify] = self._store_old_value.copy()
                self._IsPointLifted = False
                self.set_update_photo()



