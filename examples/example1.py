# -*- coding: UTF-8 -*-

'''
@created: 09.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.Qt import QWidget
    
from qtmaps.wms import OSMTileSourceA, GoogleMapsSource
from qtmaps.qt import qtTwinWmsMap
from qtmaps.qts import add_menu, vbox_layout, hbox_layout

from pal import GOOGLE_API_KEY

TEST_LOC = (11.647032, 52.139045, 19)

        
        
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('qt test app')
        add_menu(self, "File", [("Exit", lambda: sys.exit())])
        add_menu(self, "View", [("Fullscreen", lambda: self.showFullScreen()),
                                ("Maximized", lambda: self.showMaximized())])
        
        self.osmTiles = OSMTileSourceA(cachedir="../cache", download_delay=1.1)
        self.googleTiles = GoogleMapsSource(cachedir="../cache", maptype="hybrid", api_key=GOOGLE_API_KEY, download_delay=0.01)
        #self.tilesource = StamenTonerTileSource(cachedir="./cache", download_delay=1.1)
        
        
        """
        self.map1 = qtWmsMap(tilesource=self.osmTiles, initial=TEST_LOC)
        self.map2 = qtWmsMap(tilesource=self.googleTiles, initial=TEST_LOC)
        #
        self.map1.view.viewChanged.connect(self.map2.view.changeView)
        self.map1.view.scrollbarsChanged.connect(self.map2.view.changeScrollbars)
        self.map2.view.viewChanged.connect(self.map1.view.changeView)
        self.map2.view.scrollbarsChanged.connect(self.map1.view.changeScrollbars)
        #
        self.layout0 = vbox_layout(self.map1, self.map2)
        self.cw = QWidget()
        self.cw.setLayout(self.layout0)
        """
        self.cw = qtTwinWmsMap(tilesource1=self.osmTiles, tilesource2=self.googleTiles,
                              mapsize=(2*256,2*256), align="vertical", initial=TEST_LOC)
        self.setCentralWidget(self.cw)
        
        
    
    
def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    #mw.showMaximized()
    sys.exit(app.exec_())   

if __name__ == "__main__":
    main()
