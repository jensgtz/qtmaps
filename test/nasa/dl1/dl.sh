gdal_translate -of GTiff -outsize 256 256 -projwin 16 50 19 45 -projwin_srs EPSG:4326 dl.xml dl.tif
gdal_translate -of PNG dl.tif dl.png