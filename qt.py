# -*- coding: UTF-8 -*-

'''
@created: 09.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''


from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QWidget, QGraphicsView, QGraphicsScene, QPixmap,\
    QWheelEvent, QPainter, QEvent, QMouseEvent, QGraphicsSceneMouseEvent, QRectF,\
    QCursor

from qtmaps.wms import TileSource
from qtmaps.qts import vbox_layout, hbox_layout



class qtMapScene(QGraphicsScene):
    def __init__(self):
        QGraphicsScene.__init__(self)

class qtMapView(QGraphicsView):
    
    scrollbarsChanged = pyqtSignal(float, float)
    
    def __init__(self, initial=(0,0,3)):
        QGraphicsView.__init__(self)
        self.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #
        self.mapPos = initial[0:2]
        self.mapZoom = initial[2]
        self.scenePos = None   # cant use self.toScenePos(*self.mapPos)
        self.viewMode = "pan"
        self.viewAnchor = "center"  #center: (lon,lat) will be centered in view, mouse: (lon,lat) will be under mouse
        self.panPos = None
        
    def redrawMap(self):
        print("qtMapView.redrawMap()")
        scene = self.scene()
        scene.clear()
            
    def toMapPos(self, scene_x, scene_y):
        return (scene_x, scene_y)
    
    def toScenePos(self, map_x, map_y):
        return (map_x, map_y)
    
    def zoomIn(self):
        pass
    
    def zoomOut(self):
        pass
    
    def resetScrollbars(self):
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        
    def changeScrollbars(self, dx, dy):
        x = self.horizontalScrollBar().value() + dx
        self.horizontalScrollBar().setValue(x)
        y = self.verticalScrollBar().value() + dy
        self.verticalScrollBar().setValue(y)
        print("changeScrollbars(dx=%r, dy=%r): x=%r y=%r" % (dx, dy, x, y))
        
    def panXY(self, dx, dy):
        self.changeScrollbars(dx, dy)
        self.scrollbarsChanged.emit(dx, dy)
    
    def actLeftButton(self, event:QMouseEvent):
        if self.viewMode == "pan":
            #self.viewport().setCursor(QCursor(Qt.ClosedHandCursor))
            self.panPos = event.pos()
            print("pan", self.panPos)
    
    def actMiddleButton(self, event:QMouseEvent):
        pass
    
    def actRightButton(self, event:QMouseEvent):
        pass
    
    def actMouseRelease(self, event:QMouseEvent):
        if self.viewMode == "pan":
            #self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            self.panPos = None
    
    def actMouseMove(self, event:QMouseEvent):
        if self.viewMode == "pan":
            pos = event.pos()
            dp = self.panPos - pos 
            self.panXY(dx=dp.x(), dy=dp.y())
            self.panPos = pos
        
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
    
    def mouseMoveEvent(self, event:QMouseEvent):
        self.actMouseMove(event)
        
    def wheelEvent(self, event:QGraphicsSceneMouseEvent):
        self.scenePos = self.mapToScene(event.pos())
        self.mapPos = self.toMapPos(self.scenePos.x(), self.scenePos.y())
        print("wheel event.pos=%r scenePos=%r mapPos=%r" % (event.pos(), self.scenePos, self.mapPos))
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
    
    def toScenePos(self, map_x, map_y):
        return qtMapView.toScenePos(self, map_x, map_y)
    
    def redrawMap(self):
        print("qtRasterView.redrawMap()")
        scene = self.scene()
        scene.clear() 
        scene.addPixmap(self.img_pixmap)
    
    
###

class qtWMSView(qtMapView):
    
    MAX_ZOOM = 19
    
    viewChanged = pyqtSignal(float, float, int)
    
    def __init__(self, tilesource:TileSource, initial=(0,0,3)):
        qtMapView.__init__(self, initial=initial)
        self.tilesource = tilesource
        
    def toMapPos(self, scene_x, scene_y):
        return self.tilesource.pixelToCoord(pixel_x=scene_x, pixel_y=scene_y, zoom=self.mapZoom)
    
    def toScenePos(self, map_x, map_y):
        return self.tilesource.coordToPixel(lon=map_x, lat=map_y, zoom=self.mapZoom)
    
    def adjustScrollbars(self):
        """ adjust scrollbars """
        (sx, sy) = self.toScenePos(*self.mapPos)
        if self.viewAnchor == "center":
            vx, vy = self.width()/2, self.height()/2
            dx, dy = sx-vx, sy-vy
        elif self.viewAnchor == "mouse":
            pass
        else:
            raise NotImplementedError
        self.horizontalScrollBar().setValue(dx)
        self.verticalScrollBar().setValue(dy)
        
        
    def redrawMap(self):
        print("qtWMSView.redrawMap()")
        self.resetScrollbars()
        scene = self.scene()
        scene.clear()
        for row in self.tilesource.tiles:
            for tile in row:
                if tile.path is None: 
                    continue
                pixmap = QPixmap()
                pixmap.load(tile.path)
                item = scene.addPixmap(pixmap)
                item.setPos(tile.sceneX, tile.sceneY)
        self.adjustScrollbars()
        
    def update(self, *args, **kwargs):
        print("qtWMSView.update()")
        QGraphicsView.update(self, *args, **kwargs)
        #self.redrawMap()
        self.centerMap(coord=self.mapPos, zoom=self.mapZoom)
        
    def changeView(self, lon, lat, zoom):
        self.mapPos = (lon, lat)
        self.mapZoom = zoom
        vs = self.size()
        vw, vh = vs.width(), vs.height()
        self.tilesource.loadTiles(lon=lon, lat=lat, zoom=zoom, w1=vw/2, w2=vw/2, h1=vh/2, h2=vh/2)
        self.redrawMap()
        
    def centerMap(self, coord, zoom):
        self.changeView(*coord, zoom)
        self.viewChanged.emit(*coord, zoom)
    
    def zoomIn(self):
        print("zoomIn()")
        self.mapZoom = min(self.mapZoom+1, self.MAX_ZOOM)
        self.centerMap(self.mapPos, self.mapZoom)
        
    def zoomOut(self):
        print("zoomOut()")
        self.mapZoom = max(0, self.mapZoom-1)
        self.centerMap(self.mapPos, self.mapZoom)
        

          
        
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
    

class qtTwinWmsMap(QWidget):
    def __init__(self, tilesource1, tilesource2, mapsize=(256, 256), align="vertical", initial=(0,0,0)):
        QWidget.__init__(self)
        self.tileSource1 = tilesource1
        self.tileSource2 = tilesource2
        self.wmsMap1 = qtWmsMap(tilesource=self.tileSource1, initial=initial)
        self.wmsMap2 = qtWmsMap(tilesource=self.tileSource2, initial=initial)
        if mapsize:
            self.wmsMap1.setMaximumSize(*mapsize)
            self.wmsMap2.setMaximumSize(*mapsize)
            self.wmsMap1.view.resize(*mapsize)
            self.wmsMap2.view.resize(*mapsize)
        self.wmsMap1.view.viewChanged.connect(self.wmsMap2.view.changeView)
        self.wmsMap1.view.scrollbarsChanged.connect(self.wmsMap2.view.changeScrollbars)
        self.wmsMap2.view.viewChanged.connect(self.wmsMap1.view.changeView)
        self.wmsMap2.view.scrollbarsChanged.connect(self.wmsMap1.view.changeScrollbars)
        if align == "vertical":
            self.layout0 = vbox_layout(self.wmsMap1, self.wmsMap2)
        else:
            self.layout0 = hbox_layout(self.wmsMap1, self.wmsMap2)
        self.setLayout(self.layout0)
        print("map1: %r %r %r %r" % (self.wmsMap1.size(), self.wmsMap1.view.size(), self.wmsMap1.view.viewport().size(),
                                     self.wmsMap1.scene.sceneRect()))

    def centerMap(self, coord, zoom):
        self.wmsMap1.view.centerMap(coord, zoom)

# test

def test():
    pass

if __name__ == "__main__":
    test()