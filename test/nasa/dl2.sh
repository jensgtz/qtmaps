gdal_translate -of GTiff -outsize 1200 1000 -projwin -105 42 -93 32 GIBS_Aqua_MODIS_true.xml GreatPlainsSmoke1.tif
gdal_translate -of JPEG GreatPlainsSmoke1.tif GreatPlainsSmoke1.jpg