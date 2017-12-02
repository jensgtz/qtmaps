# -*- coding: UTF-8 -*-

'''
@created: 24.10.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

from configparser import ConfigParser
import re
from osgeo import ogr



TYPE_MAP = dict([("integer", ogr.OFTInteger),
                 ("float", ogr.OFTReal),
                 ("string", ogr.OFTString)])
DSTYPE_REGEX = [("\.shp$", "ESRI Shapefile")]

class OGRMap():
    
    OPEN_READONLY, OPEN_WRITEABLE = 0, 1
        
    def __init__(self):
        self.drivers = dict()
        self.datasources = dict()
        self.layers = dict()
        self.layercfg = dict()
        self.layerorder = list()
        self.srs = None
        
    def __del__(self):
        print("OGRMap.__del__()")
        self.layers.clear()
        self.datasources.clear()
        self.drivers.clear()
        
    def loadLayerCfg(self, cfg_path):
        pass
        
    def getDriver(self, datasource:str):
        drivername = None
        for pattern, name in DSTYPE_REGEX:
            if re.findall(pattern=pattern, string=datasource, flags=re.UNICODE):
                drivername = name
                break
        if drivername is None:
            return None 
        driver = ogr.GetDriverByName(drivername)
        return driver
    
    def addDataSource(self, ds_name, driver_name, conn_str, mode=OPEN_WRITEABLE):
        if not(driver_name in self.drivers):
            self.drivers[driver_name] = ogr.GetDriverByName(driver_name)
            assert self.drivers[driver_name] is not None, "%s driver not available." % driver_name
        if not(ds_name in self.datasources):
            self.datasources[ds_name] = self.drivers[driver_name].Open(conn_str, mode)
            assert self.datasources[ds_name] is not None, "Could not open %s" % conn_str
    
    def addLayer(self, layer_name, ds_name, dslayer_name=None):
        ds = self.datasources[ds_name]
        if dslayer_name:
            layer = ds.GetLayerByName(dslayer_name)
        else:
            layer = ds.GetLayer() 
        self.layers[layer_name] = layer
        self.layerorder.append(layer_name)
        #
        print("OGRMap.readLayer(): %d features" % layer.GetFeatureCount())
    
    def createLayer(self, layer_name, fields_cfg, ds_name, dslayer_name=None):
        pass
        
    def writeLayer(self, layer_name):
        pass
    
    def getLayer(self, layer_name):
        return self.layers.get(layer_name, None)
    
    def iterFeatures(self, layer_name, n=None) -> ogr.Feature:
        i = 0
        for feature in self.layers[layer_name]:
            i += 1
            yield feature
            if n: 
                if i >= n: 
                    break
    
    def addFeature(self, layername):
        pass
    

### tools

def list_drivernames():
    cnt = ogr.GetDriverCount()
    formatsList = []  # Empty List
    
    for i in range(cnt):
        driver = ogr.GetDriver(i)
        driverName = driver.GetName()
        if not driverName in formatsList:
            formatsList.append(driverName)
    
    formatsList.sort() # Sorting the messy list of ogr drivers
    
    for i in formatsList:
        print(i)

### test

def test1():
    #data has been removed
    m = OGRMap()
    m.addDataSource(ds_name="capitals_shp", driver_name="ESRI Shapefile", 
                    conn_str="examples/data/vector/CNTR_2014_60M_SH/Data/CNTR_CAPT_PT_2014.shp",
                    mode=OGRMap.OPEN_READONLY)
    m.addDataSource(ds_name="borders_shp", driver_name="ESRI Shapefile", 
                    conn_str="examples/data/vector/CNTR_2014_60M_SH/Data/CNTR_BN_60M_2014.shp", 
                    mode=OGRMap.OPEN_READONLY)
    #m.addDataSource(ds_name="substations_shp", driver_name="ESRI Shapefile",
    #                conn_str="test/substations/substations.shp",
    #                mode=OGRMap.OPEN_WRITEABLE)
    m.addLayer(layer_name="capitals", ds_name="capitals_shp", 
               dslayer_name=None)
    m.addLayer(layer_name="borders", ds_name="borders_shp", 
               dslayer_name=None)
    layer = m.getLayer("capitals")
    print(layer.GetSpatialRef().ExportToWkt())
    for feature in m.iterFeatures("capitals", n=10):
        geom = feature.GetGeometryRef()
        print(geom.Centroid().ExportToWkt())
    
        
    #m.createLayer("substations", defcfg, ds_name, dslayer_name)
        

def test():
    #list_drivernames()
    test1()
    
if __name__ == "__main__":
    test()
