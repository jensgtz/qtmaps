'''
Created on 28.11.2017

@author: uzanto
'''

from __future__ import division
import math
MERCATOR_RANGE = 256

def bound(value, opt_min, opt_max):
    if (opt_min != None): 
        value = max(value, opt_min)
    if (opt_max != None): 
        value = min(value, opt_max)
    return value


def degreesToRadians(deg):
    return deg * (math.pi / 180)


def radiansToDegrees(rad):
    return rad / (math.pi / 180)


class G_Point():
    def __init__(self,x=0, y=0):
        self.x = x
        self.y = y

class G_LatLng():
    def __init__(self,lt, ln):
        self.lat = lt
        self.lng = ln


class MercatorProjection():

    def __init__(self) :
        self.pixelOrigin_ =  G_Point( MERCATOR_RANGE / 2, MERCATOR_RANGE / 2)
        self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360
        self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2 * math.pi)


    def fromLatLngToPoint(self, latLng, opt_point=None) :
        point = opt_point if opt_point is not None else G_Point(0,0)
        origin = self.pixelOrigin_
        point.x = origin.x + latLng.lng * self.pixelsPerLonDegree_  
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.  This is about a third of a tile past the edge of the world tile.
        siny = bound(math.sin(degreesToRadians(latLng.lat)), -0.9999, 0.9999)
        point.y = origin.y + 0.5 * math.log((1 + siny) / (1 - siny)) * -     self.pixelsPerLonRadian_   
        return point


    def fromPointToLatLng(self,point) :
        origin = self.pixelOrigin_
        lng = (point.x - origin.x) / self.pixelsPerLonDegree_
        latRadians = (point.y - origin.y) / -self.pixelsPerLonRadian_
        lat = radiansToDegrees(2 * math.atan(math.exp(latRadians)) - math.pi / 2)
        return G_LatLng(lat, lng)

#pixelCoordinate = worldCoordinate * pow(2,zoomLevel)

    def getCorners(self, center:G_LatLng, zoom, mapWidth, mapHeight):
        scale = 2**zoom
        #proj = MercatorProjection()
        centerPx = self.fromLatLngToPoint(center)
        SWPoint = G_Point(centerPx.x-(mapWidth/2)/scale, centerPx.y+(mapHeight/2)/scale)
        SWLatLon = self.fromPointToLatLng(SWPoint)
        NEPoint = G_Point(centerPx.x+(mapWidth/2)/scale, centerPx.y-(mapHeight/2)/scale)
        NELatLon = self.fromPointToLatLng(NEPoint)
        return {
            'N' : NELatLon.lat,
            'E' : NELatLon.lng,
            'S' : SWLatLon.lat,
            'W' : SWLatLon.lng,
        }
        
    def bbox(self, lon, lat, zoom, width, height):
        b = self.getCorners(center=G_LatLng(lon, lat), zoom=zoom, mapWidth=width, mapHeight=height)
        (lon1, lat1, lon2, lat2) = (b["W"], b["N"], b["E"], b["S"])
        return (lon1, lat1, lon2, lat2)
    
def test1():
    centerLat = 49.141404
    centerLon = -121.960988
    zoom = 10
    mapWidth = 640
    mapHeight = 640
    proj = MercatorProjection()
    #centerPoint = MercatorProjection.G_LatLng(centerLat, centerLon)
    #centerPoint = proj.fromLatLngToPoint(G_LatLng(centerLat, centerLon))
    centerPoint = G_LatLng(centerLat, centerLon)
    corners = proj.getCorners(centerPoint, zoom, mapWidth, mapHeight)
    print(corners)

def test2():
    proj = MercatorProjection()
    for i in range(20):
        bbox = proj.bbox(lon=0, lat=0, zoom=i, width=256, height=256)
        print("zoom=%d" % i, bbox)
    
def test():
    #test1()
    test2()

    
if __name__ == '__main__':
    test()