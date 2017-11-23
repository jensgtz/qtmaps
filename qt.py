# -*- coding: UTF-8 -*-

'''
@created: 09.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QWidget, QGraphicsView, QGraphicsScene, QPixmap,\
    QWheelEvent, QPainter, QEvent, QMouseEvent, QGraphicsSceneMouseEvent, QRectF

from qtmaps.wms import TileSource
from qtmaps.qts import vbox_layout

###

class qtMapScene(QGraphicsScene):
    def __init__(self):
        QGraphicsScene.__init__(self)

class qtMapView(QGraphicsView):
    def __init__(self, initial=(0,0,3)):
        QGraphicsView.__init__(self)
        self.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #
        self.map_pos = initial[0:2]
        self.map_zoom = initial[2]
        self.scene_pos = None   # cant use self.scenePos(*self.map_pos)
    
    def redrawMap(self):
        print("qtMapView.redrawMap()")
        scene = self.scene()
        scene.clear()
            
    def mapPos(self, scene_x, scene_y):
        return (scene_x, scene_y)
    
    def scenePos(self, map_x, map_y):
        return (map_x, map_y)
    
    def zoomIn(self):
        pass
    
    def zoomOut(self):
        pass
    
    def actLeftButton(self, event:QMouseEvent):
        pass
    
    def actMiddleButton(self, event:QMouseEvent):
        pass
    
    def actRightButton(self, event:QMouseEvent):
        pass
    
    def actMouseRelease(self, event:QMouseEvent):
        pass
    
    def actWheelUp(self, event:QGraphicsSceneMouseEvent):
        self.zoomIn()
    
    def actWheelDown(self, event:QGraphicsSceneMouseEvent):
        self.zoomOut()
    
    def mousePressEvent(self, event:QMouseEvent):
        button = event.button()
        if button == Qt.LeftButton:
            self.actLeftButton(event)
        elif button == Qt.MiddleButton:
            self.actMiddleButton(event)
        elif button == Qt.RightButton:
            self.actRightButton(event)
        else:
            raise NotImplementedError
    
    def mouseReleaseEvent(self, event:QMouseEvent):
        self.actMouseRelease(event)
    
    def wheelEvent(self, event:QGraphicsSceneMouseEvent):
        self.scene_pos = self.mapToScene(event.pos())
        self.map_pos = self.mapPos(self.scene_pos.x(), self.scene_pos.y())
        if event.angleDelta().y() > 0:
            self.actWheelUp(event)
        else:
            self.actWheelDown(event)
                    
###

class qtRasterView(qtMapView):
    
    def __init__(self, img_path:str, initial=(0,0,3)):
        qtMapView.__init__(self, initial=initial)
        self.img_path = img_path
        self.img_pixmap = QPixmap(img_path)
    
    def mapPos(self, scene_x, scene_y):
        return qtMapView.mapPos(self, scene_x, scene_y)    
    
    def scenePos(self, map_x, map_y):
        return qtMapView.scenePos(self, map_x, map_y)
    
    def redrawMap(self):
        print("qtRasterView.redrawMap()")
        scene = self.scene()
        scene.clear() 
        scene.addPixmap(self.img_pixmap)
    
    
###

class qtWMSView(qtMapView):
    
    def __init__(self, tilesource:TileSource, initial=(0,0,3)):
        qtMapView.__init__(self, initial=initial)
        self.tilesource = tilesource
        
    def mapPos(self, scene_x, scene_y):
        return self.tilesource.pixelToCoord(pixel_x=scene_x, pixel_y=scene_y, zoom=self.map_zoom)
    
    def scenePos(self, map_x, map_y):
        return self.tilesource.coordToPixel(map_x=map_x, map_y=map_y, zoom=self.map_zoom)
    
    def redrawMap(self):
        print("qtWMSView.redrawMap()")
        scene = self.scene()
        scene.clear()
        for row in self.tilesource.tiles:
            for path, pos_x, pos_y, tilex, tiley in row:
                if path is None: continue
                pixmap = QPixmap()
                pixmap.load(path)
                item = scene.addPixmap(pixmap)
                item.setPos(pos_x, pos_y)
    
    def update(self, *args, **kwargs):
        print("qtWMSView.update()")
        QGraphicsView.update(self, *args, **kwargs)
        self.centerMap(coord=self.map_pos, zoom=self.map_zoom)
        
    def centerMap(self, coord, zoom):
        vs = self.size()
        vw, vh = vs.width(), vs.height()
        self.tilesource.loadTiles(lon=coord[0], lat=coord[1], zoom=zoom, w1=vw/2, w2=vw/2, h1=vh/2, h2=vh/2)
        self.redrawMap()
    
    def zoomIn(self):
        print("zoomIn()")
        self.map_zoom = min(self.map_zoom+1, 16)
        self.update()
    
    def zoomOut(self):
        print("zoomOut()")
        self.map_zoom = max(0, self.map_zoom-1)
        self.update()
          
        
class qtWmsMap(QWidget):
    def __init__(self, tilesource:TileSource, initial=(10,50,10)):
        QWidget.__init__(self)
        self.tilesource = tilesource
        self.view = qtWMSView(tilesource=self.tilesource, initial=initial)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = vbox_layout(self.view)
        self.setLayout(layout)
        self.view.update()
    
class qtExtMapView(qtWMSView):
    def __init__(self, tilesource:TileSource, initial=(10,50,10)):
        qtWMSView.__init__(self, tilesource, initial)
    

# test

def test():
    pass

if __name__ == "__main__":
    test()