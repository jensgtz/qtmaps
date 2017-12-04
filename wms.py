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

from collections import namedtuple
from threading import Thread

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

class Tile():
    def __init__(self):
        self.path = ""
        self.xtile = 0
        self.ytile = 0
        self.zoom = 0
        self.sceneX = 0
        self.sceneY = 0
        self.mapX = 0
        self.mapY = 0
        self.width = 256
        self.height = 256
        
    def sceneBBox(self):
        return (self.sceneX, self.sceneY, self.sceneX+self.width, self.sceneY+self.height)
    
    def mapBBox(self):
        pass
    
 
TileSet = namedtuple("TileSet", ["lon","lat","zoom","w1","w2","h1","h2","tiles","tilesBBox","coordsBBox","upperLeftTile"])

class ViewRequest():
    def __init__(self, coord, zoom, wait, requestID, tileSetID, created, displayed):
        self.coord = coord
        self.zoom = zoom
        self.wait = wait
        self.requestID  = requestID
        self.tileSetID  = tileSetID
        self.created    = created
        self.displayed  = displayed
        self.timeout    = 15
    def __str__(self):
        args = (self.coord, self.zoom, self.wait, self.requestID, self.tileSetID, self.displayed)
        return "ViewRequest(coord=%r, zoom=%r, wait=%r, requestID=%r, tileSetID=%r, displayed=%r)" % args
    
        
        
class TileSource():
    
    SRC_NAME = "osm_a"
    TILE_URL = "http://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    def __init__(self, name, cachedir, download_delay=1):
        self.name = name
        self.cachedir = cachedir
        self.download_delay = download_delay
        self.src_name_args = None
        self.last_download = time.time()
        self.tileSets = []
        self.tileSetID = None 
        self.tileWidth = 256
        self.tileHeight = 256
        self.requestsCount = 0
        
    def getName(self):
        return self.name
    
    def getTileUrl(self, tilex, tiley, zoom):
        return self.TILE_URL.format(x=tilex, y=tiley, z=zoom)
    
    def getTilePath(self, tilex, tiley, zoom):
        if self.src_name_args:
            src_name = self.SRC_NAME.format(**self.src_name_args)
        else:
            src_name = self.SRC_NAME
        tile_dir = os.path.join(self.cachedir, src_name, str(zoom), str(tilex))
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
            print("... from %r" % url)
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
    
    def getTilesBBox(self, lon, lat, zoom, w1, w2, h1, h2):
        pass

    def addTileSet(self, tileset:TileSet) -> int:
        self.tileSets.append(tileset)
        return len(self.tileSets)-1
    
    def setActiveTileSet(self, tilesetid:int):
        assert tilesetid in range(len(self.tileSets))
        self.tileSetID = tilesetid
        
    def getActiveTileSet(self) -> TileSet:
        return self.tileSets[self.tileSetID]
    
    def _loadTiles(self, lon, lat, zoom, w1, w2, h1, h2):
        """ returns TilesSet """
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
        tilesBBox = (btx-nw, bty-nn, btx+ne, bty+ns)
        tilesBBox = tuple([int(x) for x in smopy.correct_box(box=tilesBBox, z=zoom)])
        # coords bbox
        (lat1, lon1) = smopy.num2deg(xtile=tilesBBox[0], ytile=tilesBBox[1], zoom=zoom)
        (lat2, lon2) = smopy.num2deg(xtile=tilesBBox[2]+1, ytile=tilesBBox[3]+1, zoom=zoom)
        coordsBBox = (lon1, lat1, lon2, lat2)
        # provide tiles
        tiles = []
        ix = 0
        for xtile in range(tilesBBox[0], tilesBBox[2]+1):
            tilesrow = []
            iy = 0
            for ytile in range(tilesBBox[1], tilesBBox[3]+1):
                lat, lon = smopy.num2deg(xtile, ytile, zoom)
                #
                tile = Tile()
                tile.path   = self.provideTile(xtile, ytile, zoom)
                tile.xtile  = xtile
                tile.ytile  = ytile
                tile.zoom   = zoom
                tile.sceneX = ix * tw
                tile.sceneY = iy * th
                tile.mapX   = lon
                tile.mapY   = lat
                #  
                tilesrow.append(tile)
                iy += 1
            tiles.append(tilesrow)
            ix += 1
        upperLeftTile = tiles[0][0]
        tileSet = TileSet(lon, lat, zoom, w1, w2, h1, h2, tiles, tilesBBox, coordsBBox, upperLeftTile)
        return tileSet
    
    def createRequestID(self):
        self.requestsCount += 1
        return self.requestsCount
    
    def _requestTilesRun(self, requestID, args, callback):
        tileset = self._loadTiles(*args)
        tileSetID = self.addTileSet(tileset)
        callback(requestID, tileSetID)
    
    def requestTiles(self, lon, lat, zoom, w1, w2, h1, h2, callback):
        """ loads tiles in background thread 
            when finished callback is executed with args requestID, tileSetID 
        """
        requestID = self.createRequestID()
        args = (lon, lat, zoom, w1, w2, h1, h2)
        thread = Thread(target=self._requestTilesRun, args=(requestID, args, callback))
        thread.daemon = True
        thread.start()
        return requestID
    
    def loadTiles(self, lon, lat, zoom, w1, w2, h1, h2):
        """ loads tiles immediately """
        print("loadTiles(lon=%r, lat=%r, zoom=%r, w1=%r, w2=%r, h1=%r, h2=%r)" % (lon, lat, zoom, w1, w2, h1, h2))
        tileSet = self._loadTiles(lon, lat, zoom, w1, w2, h1, h2)
        tileSetID = self.addTileSet(tileSet)
        self.setActiveTileSet(tileSetID)
        
    def pixelToCoord(self, pixel_x, pixel_y, zoom):
        tileSet = self.getActiveTileSet() 
        xtilef = tileSet.upperLeftTile.xtile + pixel_x / self.tileWidth  
        ytilef = tileSet.upperLeftTile.ytile + pixel_y / self.tileHeight
        (lat, lon) = smopy.num2deg(xtilef, ytilef, zoom)
        return (lon, lat)
    
    def coordToPixel(self, lon, lat, zoom):
        tileSet = self.getActiveTileSet()
        (xtilef, ytilef) = smopy.deg2num(latitude=lat, longitude=lon, zoom=zoom, do_round=False)
        x = (xtilef - tileSet.upperLeftTile.xtile) * self.tileWidth
        y = (ytilef - tileSet.upperLeftTile.ytile) * self.tileHeight
        return (x, y)
        
    
    
        
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
        #cmd = ["gdal_translate", "-of", "GTiff", "-outsize", str(self.tileWidth), 
        #       str(self.tileHeight), "-projwin", -105 42 -93 32 '<GDAL_WMS><Service name="TMS"><ServerUrl>https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Aqua_CorrectedReflectance_TrueColor/default/2013-08-21/250m/${z}/${y}/${x}.jpg</ServerUrl></Service><DataWindow><UpperLeftX>-180.0</UpperLeftX><UpperLeftY>90</UpperLeftY><LowerRightX>396.0</LowerRightX><LowerRightY>-198</LowerRightY><TileLevel>8</TileLevel><TileCountX>2</TileCountX><TileCountY>1</TileCountY><YOrigin>top</YOrigin></DataWindow><Projection>EPSG:4326</Projection><BlockSizeX>512</BlockSizeX><BlockSizeY>512</BlockSizeY><BandsCount>3</BandsCount></GDAL_WMS>' GreatPlainsSmoke2.tif
        
        #gdal_translate -of JPEG GreatPlainsSmoke2.tif GreatPlainsSmoke2.jpg"""


class OSMTileSource(TileSource):
    SRC_NAME    = "osm"
    TILE_URL    = "http://{subdomain}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    SUBDOMAINS  = ["a","b","c"]
    
    def __init__(self, name, cachedir, download_delay=0.33):
        TileSource.__init__(self, name=name, cachedir=cachedir, download_delay=download_delay)
        self.subdomainIndex = 0
    
    def getTileUrl(self, tilex, tiley, zoom):
        self.subdomainIndex += 1
        if self.subdomainIndex >= len(self.SUBDOMAINS):
            self.subdomainIndex = 0
        subdomain = self.SUBDOMAINS[self.subdomainIndex]
        return self.TILE_URL.format(subdomain=subdomain, x=tilex, y=tiley, z=zoom)
        
        
class GoogleMapsSource(TileSource):
    SRC_NAME = "google-{maptype}"
    TILE_URL = "https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&maptype={maptype}&size=256x256&key={key}"
    
    def __init__(self, name, cachedir, maptype, api_key, download_delay=1):
        TileSource.__init__(self, name=name, cachedir=cachedir, download_delay=download_delay)
        self.maptype = maptype
        self.api_key = api_key
        self.src_name_args = dict(maptype=maptype)
        
    def getTileUrl(self, tilex, tiley, zoom):
        lat, lon = smopy.num2deg(tilex+0.5, tiley+0.5, zoom)
        return self.TILE_URL.format(lon=lon, lat=lat, zoom=zoom, maptype=self.maptype, key=self.api_key)
        
        

# test

def test():
    pass

if __name__ == "__main__":
    test()