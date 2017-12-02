# -*- coding: UTF-8 -*-

'''
@created: 28.11.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

import os
import math
import subprocess
from urllib.request import urlretrieve

from pal import GOOGLE_API_KEY



MAPTYPES = ["roadmap", "satellite", "hybrid", "terrain"]



def bbox2mapargs(lon1, lat1, lon2, lat2, width=256, height=256):
    lon = (lon1+lon2)/2
    lat = (lat1+lat2)/2
    height = (lat2-lat1)/(lon2-lon1) * width
    mapargs = dict()
    return mapargs

def mapargs2bbox(lon, lat, zoom, width, height):
    MR = 256
    ppld = MR/360
    pplr = MR/(2*math.pi)
    scale = 2**zoom
    ox, oy = MR/2, MR/2
    cx = ox + lon * ppld
    siny = min(max(-0.999999, math.sin(lat * math.pi/180)), 0.999999)
    cy = oy - 0.5 * pplr * math.log((1 + siny) / (1 - siny))
    wx = cx - width / (2*scale)
    sy = cy + height / (2*scale)
    ex = cx + width / (2*scale)
    ny = cy - height / (2*scale)
    lon1 = (wx - ox) / ppld
    lat1 = (2*math.atan(math.exp((oy - ny) / pplr)) - math.pi/2)*(180/math.pi)
    lon2 = (ex - ox) / ppld
    lat2 = (2*math.atan(math.exp((oy - sy) / pplr)) - math.pi/2)*(180/math.pi)
    return (lon1, lat1, lon2, lat2)

def download_map(basedir, lon, lat, zoom, maptype="satellite", width=256, height=256):
    url_template = "https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&maptype={maptype}&size={width}x{height}&key={key}"
    url = url_template.format(lon=lon, lat=lat, zoom=zoom, maptype=maptype, width=width, height=height, key=GOOGLE_API_KEY)
    path = os.path.join(basedir, "test.png")
    urlretrieve(url, path)
    return path
     
     

# test

def test1():
    path = download_map(basedir=".", lon=10.5, lat=50, zoom=18, maptype="hybrid")
    subprocess.call(["xdg-open", path])

def test2():
    bbox = mapargs2bbox(lon=10.5, lat=50, zoom=18, width=256, height=256)
    print(bbox)
    #(10.49931335449219, 50.000441365198704, 10.500686645507814, 49.99955863074936)
    #10.498809814453125 50.0006777572 10.50018310546875 49.9997950271

def test3():
    mapargs = bbox2mapargs(10.4,49.9,10.6,50.1)
    path = download_map(basedir=".", maptype="hybrid", **mapargs)
    subprocess.call(["xdg-open", path])
    
def test():
    test1()
    #test2()
    #test3()
    
    
if __name__ == "__main__":
    test()
