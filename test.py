# -*- coding: UTF-8 -*-

'''
@created: 12.11.2017
@author : Jens Götze
@license: BSD
'''

import os
import sys
import math
import random
from collections import OrderedDict
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.Qt import QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,\
    QMouseEvent, QGraphicsSceneMouseEvent, QPoint, QFileDialog, QInputDialog,\
    QMessageBox, QRectF, QPen, QCursor, QGraphicsItemGroup, QGraphicsEllipseItem,\
    QGraphicsTextItem, QGraphicsSimpleTextItem, QPainter, QRect

import pylib3.qt5.shortcuts as qts
from pylib3.qt5.drawstyles import PEN_STYLE

def nop(*args, **kwargs):
    pass

class AppIface():
    def __init__(self):
        self.application = None
        self.mainwindow = None
        
###

class Feature():
    def __init__(self, ftype=None, geom=[], pos=None, attr=dict()):
        self.fid = None
        self.ftype = ftype
        self.geom = geom
        self.pos = pos
        self.attr = attr
    
    def toDict(self):
        return dict(fid=self.fid, ftype=self.ftype, geom=self.geom, pos=self.pos, attr=self.attr)
    
    @classmethod
    def fromDict(cls, d):
        feature = cls(fid=d.get("fid", None), ftype=d.get("ftype", None), 
                      geom=d.get("geom", []), pos=d.get("pos", None), attr=d.get("attr", {}))
        return feature
    
    def addPoint(self, coord):
        print("Feature.addPoint(%r)" % (coord,))
        print("pos=%r, geom=%r" % (self.pos, self.geom))
        if len(self.geom) == 0:
            self.pos = coord
            self.geom.append((0,0))
        else:
            self.geom.append((coord[0]-self.pos[0], coord[1]-self.pos[1]))
        
    
    def removeLastPoint(self):
        self.geom.pop()
    
    def resetGeometry(self):
        self.geom = []
        
    def finishGeometry(self):
        pass


class FeatureStore():
    def __init__(self):
        self.path = None
        self.features = []
        
    def reset(self):
        self.features = []
        
    def randomCreatePoints(self, rect, n):
        for i in range(n):
            p = (random.uniform(rect[0], rect[2]), random.uniform(rect[1], rect[3]))
            feature = Feature(ftype="point", pos=p, geom=[(0,0)])
            self.add(feature)
            
    def writeJson(self, path):
        feature_dicts = [x.toJson() for x in self.features]
        f = open(path, "w")
        f.write(json.dumps(feature_dicts))
        f.close()
        self.path = path
    
    def readJson(self, path):
        f = open(path, "r")
        s = f.read()
        f.close()
        for feature_dict in json.loads(s):
            self.add(Feature.fromDict(feature_dict))
        self.path = path
        
    def add(self, feature:Feature):
        feature.fid = len(self.features)+1
        self.features.append(feature)

    def iterFeatures(self):
        for feature in self.features:
            yield feature
            
###
  
class qtFeature(QGraphicsItem):
    
    def __init__(self, feature):
        QGraphicsItem.__init__(self)
        self._feature = feature
        self._boundingrect = QRectF(0,0,0,0)
    
    def addPoint(self, scene_pos):
        self._feature.addPoint((scene_pos.x(), scene_pos.y()))
        
    def removeLastPoint(self):
        self._feature.removeLastPoint()
        
    def finishGeometry(self):
        self._feature.finishGeometry()
        
    def onCreateMousePress(self, scene_pos, event:QMouseEvent):
        print("qtFeature.onCreateMousePress()")
        button = event.button()
        if button == Qt.LeftButton:
            self.addPoint(scene_pos)
        elif button == Qt.MiddleButton:
            self.removeLastPoint()
        elif button == Qt.RightButton:
            self.finishGeometry()
        else:
            raise NotImplementedError
        #self.update()
    
    def onCreateMouseRelease(self, scene_pos, event:QMouseEvent):
        #print("qtFeature.onCreateMouseRelease()")
        pass
    
    def onCreateMouseMove(self, scene_pos, event:QMouseEvent):
        #print("qtFeature.onCreateMouseMove()")
        pass
    

class qtPointFeature(qtFeature):
    FTYPE = "point"
    
    def paint(self, painter:QPainter, *args, **kwargs):
        print("qtPointFeature.paint()", self._feature.fid)
        d = 10
        r = 0.5 * d 
        point_rect = QRectF(-r, -r, d, d)
        painter.drawEllipse(point_rect)
        text_rect = painter.drawText(QRectF(d,-r,d+100,-r+50), Qt.AlignLeft | Qt.AlignTop, str(self._feature.fid))
        self._boundingrect = point_rect | text_rect
        
    def boundingRect(self, *args, **kwargs):
        return self._boundingrect
    
class qtLineFeature(qtFeature):
    FTYPE = "line"
    
class qtPolygonFeature(qtFeature):
    FTYPE = "polygon"

QTFEATURES = [qtPointFeature, qtLineFeature, qtPolygonFeature]
QTFEATURESDICT = dict([(x.FTYPE, x) for x in QTFEATURES])

###

class qtDrawingScene(QGraphicsScene):
    def __init__(self):
        QGraphicsScene.__init__(self)

###

class qtDrawingView(QGraphicsView):
    
    def __init__(self, featurestore:FeatureStore):
        QGraphicsView.__init__(self)
        self.featurestore = featurestore
        self.feature = None
        self.qtfeature = None
        self.ftype = None
        self.mode = None
        self.lastPos = None
        self.gridOn = True
        self.setSceneRect(QRectF(0,0,1500,1500))
        """
        self.setMouseTracking(True)
        self.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
        #self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setDragMode(QGraphicsView.NoDrag)
        #self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        """
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setMouseTracking(True)
        self.setMode("add", "point")
        
    def storeFeature(self):
        self.featurestore.add(self.feature)
        self.feature = Feature(ftype=self.feature)
        self.update()
        
    def setMode(self, mode, ftype=None):
        print("qtDrawingView.setMode(mode=%r, ftype=%r)" % (mode, ftype))
        self.mode = mode
        self.ftype = ftype
        self.lastPos = None
        if mode == "add":
            self.viewport().setCursor(QCursor(Qt.CrossCursor))
            self.feature = Feature(ftype=ftype)
            self.qtfeature = None
        elif mode == "pan":
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
        elif mode == "select":
            self.viewport().setCursor(QCursor(Qt.ArrowCursor))
        else:
            raise NotImplementedError
        
        
    def drawGrid(self, delta=50):
        scene = self.scene()
        pen = QPen()
        pen.setStyle(PEN_STYLE["dot"])
        sr = self.sceneRect()
        sh = sr.height()
        sw = sr.width() 
        n_rows = math.ceil(sh / delta)
        n_columns = math.ceil(sw / delta)
        for ir in range(n_rows+1):
            y = ir*delta
            scene.addLine(0, y, sw, y, pen=pen)
        for ic in range(n_columns+1):
            x = ic*delta
            scene.addLine(x, 0, x, sh, pen=pen)
            
    def redraw(self):
        print("qtDrawingView.redraw()")
        scene = self.scene()
        for item in scene.items():
            scene.removeItem(item)
        scene.clear()
        if self.gridOn:
            self.drawGrid()
        for feature in self.featurestore.iterFeatures():
            qtfeature = QTFEATURESDICT[feature.ftype](feature=feature)
            qtfeature.setPos(*feature.pos)
            scene.addItem(qtfeature)
        if self.qtfeature:
            print("#1", self.qtfeature.scene())
            scene.addItem(self.qtfeature)
    
    def update(self, *args, **kwargs):
        QGraphicsView.update(self, *args, **kwargs)
        self.redraw()
    
    def panXY(self, dx, dy):
        x = self.horizontalScrollBar().value()
        self.horizontalScrollBar().setValue(x + dx)
        y = self.verticalScrollBar().value()
        self.verticalScrollBar().setValue(y + dy)
        
    ### zoom
    
    def zoomIn(self):
        self.scale(1.1, 1.1)
    
    def zoomOut(self):
        self.scale(0.9, 0.9)
        
    def resetZoom(self):
        self.resetTransform()
        
    def zoomBestFit(self):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    ### actions
    
    def actLeftButton(self, event:QMouseEvent):
        pos = self.mapToScene(event.pos())
        if self.mode == "add":
            self.feature.addCoord(coord=(pos.x(), pos.y()))
            
    def actMiddleButton(self, event:QMouseEvent):
        self.feature.resetGeometry()
    
    def actRightButton(self, event:QMouseEvent):
        self.feature.finishGeometry()
    
    def actMouseRelease(self, event:QMouseEvent):
        pass
    
    def actWheelUp(self, event:QGraphicsSceneMouseEvent):
        self.zoomIn()
    
    def actWheelDown(self, event:QGraphicsSceneMouseEvent):
        self.zoomOut()
    
    def mousePressEvent(self, event:QMouseEvent):
        print("qtDrawingView.mousePressEvent(): mode=%r" % self.mode)
        view_pos = event.pos()
        scene_pos = self.mapToScene(view_pos)
        button = event.button()
        if self.mode == "add":
            if self.qtfeature is None:
                self.qtfeature = QTFEATURESDICT[self.ftype](feature=self.feature)
                self.qtfeature.setPos(scene_pos)
                self.scene().addItem(self.qtfeature)
            self.qtfeature.onCreateMousePress(scene_pos, event)
            self.update()
        elif self.mode == "pan" and button == Qt.LeftButton:
            self.viewport().setCursor(QCursor(Qt.ClosedHandCursor))
            self.lastPos = view_pos
        elif self.mode == "select" and button == Qt.LeftButton:
            pass
        else:
            pass
        return QGraphicsView.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event:QMouseEvent):
        print("qtDrawingView.mouseReleaseEvent(): mode=%r" % self.mode)
        scene_pos = self.mapToScene(event.pos())
        button = event.button()
        if self.mode == "add" and self.qtfeature:
            self.qtfeature.onCreateMouseRelease(scene_pos, event)
        elif self.mode == "pan" and button == Qt.LeftButton:
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            self.lastPos = None
        elif self.mode == "select" and button == Qt.LeftButton:
            pass
        else:
            pass
        return QGraphicsView.mouseReleaseEvent(self, event)
    
    def mouseMoveEvent(self, event:QMouseEvent):
        #print("qtDrawingView.mousePressEvent(): mode=%r" % self.mode)
        view_pos = event.pos()
        scene_pos = self.mapToScene(view_pos)
        if self.mode == "add" and self.qtfeature:
            self.qtfeature.onCreateMouseMove(scene_pos, event)
        elif self.mode == "pan" and self.lastPos:
            dp = self.lastPos - view_pos 
            self.panXY(dx=dp.x(), dy=dp.y())
            self.lastPos = view_pos
        else:
            pass
        return QWidget.mouseMoveEvent(self, event)
        
    def wheelEvent(self,event:QGraphicsSceneMouseEvent):
        if event.angleDelta().y() > 0:
            self.actWheelUp(event)
        else:
            self.actWheelDown(event)
        QGraphicsView.wheelEvent(self, event)
 
 
        
class qtDrawingBoard(QWidget):
    def __init__(self, api:AppIface, featurestore:FeatureStore):
        QWidget.__init__(self)
        self.api = api
        self.featurestore = featurestore
        self.initUI()
        
    def initUI(self):
        self.scene = qtDrawingScene()
        self.view = qtDrawingView(featurestore=self.featurestore)
        self.view.setScene(self.scene)
        self.setLayout(qts.vbox_layout(self.view))
        self.toolbar = qts.actionstoolbar(actions=[("icon:gnome/16/zoom-out", lambda: self.view.zoomOut()),
                                                   ("icon:gnome/16/zoom-original", lambda: self.view.resetZoom()),
                                                   ("icon:gnome/16/zoom-best-fit", lambda: self.view.zoomBestFit()),
                                                   ("icon:gnome/16/zoom-in", lambda: self.view.zoomIn()),
                                                   ("icon:grass/pan", lambda: self.view.setMode("pan")),
                                                   ("icon:grass/select", lambda: self.view.setMode("select")),
                                                   ("icon:grass/point-create", lambda: self.view.setMode("add", "point")),
                                                   ("icon:grass/line-create", lambda: self.view.setMode("add", "line")),
                                                   ("icon:grass/polygon-create", lambda: self.view.setMode("add", "polygon")),
                                                   ("icon:grass/settings", self.actSettings),
                                                   ("icon:grass/redraw", lambda: self.view.update())]) 
        self.api.mainwindow.addToolBar(self.toolbar)
        self.view.update()
        
    def actSettings(self):
        pass
    
        
        
class MainWindow(QMainWindow):
    def __init__(self, api:AppIface):
        QMainWindow.__init__(self)
        self.api = api
        self.api.mainwindow = self
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('qt test app')
        qts.add_menu(self, "File", [("New", self.actNew),
                                    ("Open", self.actOpen),
                                    ("Save", self.actSave),
                                    ("SaveAs", self.actSaveAs),
                                    ("Exit", self.actExit)])
        qts.add_menu(self, "View", [("Fullscreen", lambda: self.showFullScreen()),
                                    ("Maximized", lambda: self.showMaximized())])
        self.featurestore = FeatureStore()
        self.featurestore.randomCreatePoints(rect=[0,0,1500,1500], n=5)
        self.drawingboard = qtDrawingBoard(api=self.api, featurestore=self.featurestore)
        self.setCentralWidget(self.drawingboard)
        
    def actNew(self):
        self.featurestore.reset()
    
    def actOpen(self):
        path, ok = QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), '*.json')
        if not(ok): return
        self.featurestore.readJson(path)
    
    def actSave(self):
        if self.featurestore.path is None:
            self.actSaveAs()
        else:
            self.featurestore.writeJson(self.featurestore.path)
    
    def actSaveAs(self):
        path, ok = QFileDialog.getSaveFileName(self, 'Save File', os.getcwd(), '*.json')
        if not(ok): return
        self.featurestore.writeJson(path)
    
    def actExit(self):
        answer = QMessageBox.question(self, "Exit", "Save changes ?")
        if answer == QMessageBox.Yes:
            self.actSave()
        sys.exit()
        
    
    
def main():
    app = QApplication(sys.argv)
    api = AppIface()
    api.application = app 
    mw = MainWindow(api)
    mw.showMaximized()
    sys.exit(app.exec_())   

if __name__ == "__main__":
    main()
