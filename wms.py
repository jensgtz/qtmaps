# -*- coding: UTF-8 -*-

'''
@created: 10.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD

google satelite
http://mt1.google.com/vt/lyrs=y&x=8&y=8&z=9

https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+API+for+Developers
https://wiki.earthdata.nasa.gov/display/GIBS/Map+Library+Usage#expand-GDALBasics
https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+Available+Imagery+Products#expand-CorrectedReflectance16Products
'''

import smopy
import time
import os
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
import numpy as np
import subprocess


###

def now():
    return time.time()

class TileSource():
    
    SRC_NAME = "osm_a"
    TILE_URL = "http://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    def __init__(self, cachedir, download_delay=1):
        self.cachedir = cachedir
        self.download_delay = download_delay
        self.tile_path = None
        self.tiles = []
        self.last_download = time.time() 
        self.tile_width = 256
        self.tile_heith = 256
        
    def getTileUrl(self, tilex, tiley, zoom):
        return self.TILE_URL.format(x=tilex, y=tiley, z=zoom)
    
    def getTilePath(self, tilex, tiley, zoom):
        tile_dir = os.path.join(self.cachedir, self.SRC_NAME, str(zoom), str(tilex))
        tile_fn = str(tiley)+".png"
        tile_path = os.path.join(tile_dir, tile_fn)
        return (tile_dir, tile_fn, tile_path)
    
    def downloadTile(self, tilex, tiley, zoom):
        print("downloading tile (x=%r, y=%r, z=%r) ..." % (tilex, tiley, zoom))
        (tile_dir, tile_fn, tile_path) = self.getTilePath(tilex, tiley, zoom)
        url = self.getTileUrl(tilex, tiley, zoom)
        if not(os.path.exists(tile_dir)):
            os.makedirs(tile_dir)
        # wait if necessary
        current_time = time.time()
        time_left = current_time - self.last_download
        if time_left < self.download_delay:
            time.sleep(self.download_delay - time_left) 
        #
        try:
            urlretrieve(url, tile_path)
            ret = tile_path
        except (URLError, HTTPError) as e:
            print(e)
            #print("error code:", e.code)
            #print("error reason:", e.reason)
            ret = None
        self.last_download = time.time()
        return ret
    
    def provideTile(self, tilex, tiley, zoom):
        #print("provideTile(tilex=%r, tiley=%r, zoom=%r)" % (tilex, tiley, zoom))
        (tile_dir, tile_fn, tile_path) = self.getTilePath(tilex, tiley, zoom)
        if not(os.path.exists(tile_path)):
            ret = self.downloadTile(tilex, tiley, zoom)
        else:
            ret = tile_path
        return ret
    
    def getTileByCoords(self, lon, lat, zoom):
        (x, y) = smopy.deg2num(lat, lon, zoom, do_round=True)
        return self.provideTile(x, y, zoom)
    
    def loadTiles(self, lon, lat, zoom, w1, w2, h1, h2):
        print("loadTiles(lon=%r, lat=%r, zoom=%r, w1=%r, w2=%r, h1=%r, h2=%r)" % (lon, lat, zoom, w1, w2, h1, h2))
        # tile width and height
        tw = 256
        th = 256
        # view port width and height
        vw = w1+w2
        vh = h1+h2
        # base tile (float, int, relative from upper-left corner)
        (btxf, btyf) = smopy.deg2num(latitude=lat, longitude=lon, zoom=zoom, do_round=False)
        btx, bty = int(btxf), int(btyf) 
        btxr, btyr = np.modf(btxf)[0], np.modf(btyf)[0]
        # number of extra tiles in directions N, E, S, W
        nn = np.ceil(h1/th - btyr)
        ne = np.ceil(w2/tw - (1-btxr))
        ns = np.ceil(h2/th - (1-btyr))
        nw = np.ceil(w1/tw - btxr)
        #print("nn=%r, ne=%r, ns=%r, nw=%r" % (nn, ne, ns, nw))
        # tiles bbox
        tiles_bbox = (btx-nw, bty-nn, btx+ne, bty+ns)
        tiles_bbox = [int(x) for x in smopy.correct_box(box=tiles_bbox, z=zoom)]
        #print("tiles_bbox", tiles_bbox)
        # coords bbox
        coords_bbox = (*smopy.num2deg(xtile=tiles_bbox[0], ytile=tiles_bbox[1], zoom=zoom),
                       *smopy.num2deg(xtile=tiles_bbox[2]+1, ytile=tiles_bbox[3]+1, zoom=zoom))
        #viewport upper-left
        
        #insert upper-left
                
        # provide tiles
        self.tiles = []
        ix = 0
        for tilex in range(tiles_bbox[0], tiles_bbox[2]+1):
            tilesrow = []
            iy = 0
            for tiley in range(tiles_bbox[1], tiles_bbox[3]+1):
                tile_path = self.provideTile(tilex, tiley, zoom)
                tile_x = ix * tw
                tile_y = iy * th
                tilesrow.append((tile_path, tile_x, tile_y, tilex, tiley))
                iy += 1
            self.tiles.append(tilesrow)
            ix += 1
        
    def pixelToCoord(self, pixel_x, pixel_y, zoom):
        ultile = self.tiles[0][0]
        xtilef = ultile[3] + pixel_x / self.tile_width  
        ytilef = ultile[4] + pixel_y / self.tile_heith
        (lat, lon) = smopy.num2deg(xtilef, ytilef, zoom)
        return (lon, lat)
    
    def coordToPixel(self, lon, lat, zoom):
        pass
    
    
        
class OSMTileSourceA(TileSource):
    SRC_NAME = "osm-a"
    TILE_URL = "http://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
    
class OSMTileSourceB(TileSource):
    SRC_NAME = "osm-b"
    TILE_URL = "http://b.tile.openstreetmap.org/{z}/{x}/{y}.png"
        
class OSMTileSourceC(TileSource):
    SRC_NAME = "osm-c"
    TILE_URL = "http://C.tile.openstreetmap.org/{z}/{x}/{y}.png"
        
class StamenTonerTileSource(TileSource):
    SRC_NAME = "stamen-toner"
    TILE_URL = "http://a.tile.stamen.com/toner/{z}/{x}/{y}.png"
      
class NASAEarthdataSource(TileSource):
    SRC_NAME = "nasa-earth"
    TILE_URL = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{Time}/{TileMatrixSet}/{ZoomLevel}/{TileRow}/{TileCol}.png"
    
    def downloadTile(self, tilex, tiley, zoom):
        pass
        #cmd = ["gdal_translate", "-of", "GTiff", "-outsize", str(self.tile_width), 
        #       str(self.tile_height), "-projwin", -105 42 -93 32 '<GDAL_WMS><Service name="TMS"><ServerUrl>https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Aqua_CorrectedReflectance_TrueColor/default/2013-08-21/250m/${z}/${y}/${x}.jpg</ServerUrl></Service><DataWindow><UpperLeftX>-180.0</UpperLeftX><UpperLeftY>90</UpperLeftY><LowerRightX>396.0</LowerRightX><LowerRightY>-198</LowerRightY><TileLevel>8</TileLevel><TileCountX>2</TileCountX><TileCountY>1</TileCountY><YOrigin>top</YOrigin></DataWindow><Projection>EPSG:4326</Projection><BlockSizeX>512</BlockSizeX><BlockSizeY>512</BlockSizeY><BandsCount>3</BandsCount></GDAL_WMS>' GreatPlainsSmoke2.tif
        
        #gdal_translate -of JPEG GreatPlainsSmoke2.tif GreatPlainsSmoke2.jpg"""
        
        
              
# test

def test():
    pass

if __name__ == "__main__":
    test()