# -*- coding: UTF-8 -*-

'''
@created: 28.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''
import shutil
import PIL
from smopy import num2deg, deg2num
import subprocess

from qtmaps.wms import TileSource, OSMTileSourceA
from qtmaps.qt import qtWmsMap
from qtmaps.googlestaticmaps import mapargs2bbox, download_map


# test

def test1():
    lon, lat = 10.5, 50
    zoom = 18
    tilex,tiley = deg2num(lat, lon, zoom, do_round=True)
    lat1,lon1 = num2deg(tilex, tiley, zoom)
    lat2,lon2 = num2deg(tilex+1, tiley+1, zoom)
    #mlon, mlat = (lon1+lon2)/2, (lat1+lat2)/2
    mlat, mlon = num2deg(tilex+0.5, tiley+0.5, zoom)
    print("bbox:", lon1, lat1, lon2, lat2)
    print("center:", mlon, mlat)
    osm = OSMTileSourceA(cachedir="./cache", download_delay=1)
    osm_path = osm.provideTile(tilex, tiley, zoom)
    print("osm_path", osm_path)
    shutil.copy(osm_path, "./map_osm.png")
    goo_path = download_map(basedir=".", lon=mlon, lat=mlat, zoom=zoom, maptype="hybrid", width=256, height=256)
    print("goo_path", goo_path)
    shutil.copy(goo_path, "./map_google.png")
    #subprocess.call(["pinta", osm_path, goo_path])
    im1 = PIL.Image.open(osm_path)
    im2 = PIL.Image.open(goo_path)
    im1 = im1.convert(mode="RGB")
    im2 = im2.convert(mode="RGB")
    im3 = PIL.Image.blend(im1, im2, 0.5)
    #im3 = PIL.Image.new("RGBA", im1.size)
    #mas = PIL.Image.new("RGBA", im1.size, (0,0,0,0.5))
    #im3 = PIL.Image.alpha_composite(im3, im1)
    #im3 = PIL.Image.alpha_composite(im3, im2)
    im3.save("./maps.png")
    
    

def test2():
    pass
        

def test3():
    import sys
    from PyQt5.Qt import QApplication, QMainWindow, QWidget
    import pylib3.qt5.shortcuts as qts
    
    class MainWindow(QMainWindow):
        
        def __init__(self):
            QMainWindow.__init__(self)
            self.osmTiles = OSMTileSourceA(cachedir="./cache")
            self.osmMap = qtWmsMap(tilesource=self.osmTiles, initial=(10.5, 50, 18))
            self.layout0 = qts.vbox_layout(self.osmMap)
            self.cw = QWidget()
            self.cw.setLayout(self.layout0)
            self.setCentralWidget(self.cw)
            
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test1()
    