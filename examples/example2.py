# -*- coding: UTF-8 -*-

'''
@created: 11.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from qtmaps.wms import OSMTileSourceA
from qtmaps.ogr import OGRMap
from qtmaps.qt import qtWmsMap
from qtmaps.qts import add_menu


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('qt test app')
        add_menu(self, "File", [("Exit", lambda: sys.exit())])
        add_menu(self, "View", [("Fullscreen", lambda: self.showFullScreen()),
                                ("Maximized", lambda: self.showMaximized())])
        
        self.tilesource = OSMTileSourceA(cachedir="./cache", download_delay=1.1)
        #self.tilesource = StamenTonerTileSource(cachedir="./cache", download_delay=1.1)
        
        self.ogrmap = OGRMap()
        self.ogrmap.addLayer(name="capitals", datasource="data/vector/CNTR_2014_60M_SH/Data/CNTR_BN_60M_2014.shp")
        
        self.mapwidget = qtWmsMap(tilesource=self.tilesource, initial=(-18.5641420746, 64.9327505996, 5))
        
        self.setCentralWidget(self.mapwidget)
        
        

def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
