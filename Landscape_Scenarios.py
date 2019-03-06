
import numpy as np
np.set_printoptions(suppress=True)

import gdal, os

import psycopg2

import subprocess 

import nlmpy

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=localhost port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

cursor.execute("""SELECT ST_MetaData(rast) As md FROM stream_network.rlp_stream_rast_testarea_50x50;""")
raster_MD = cursor.fetchall()
raster_MD = [float(xx) for xx in raster_MD[0][0][1:-1].split(',')]

nCOL = int(raster_MD[2])
nROW = int(raster_MD[3])

grid = np.zeros((nCOL, nROW))
    
X_DIM = np.arange(grid.shape[0])
Y_DIM = np.arange(grid.shape[1])

X_ll = raster_MD[0]
Y_ll = raster_MD[1]

cellSIZE = raster_MD[4]

vsipath = '/vsimem/from_postgis'

ds = band = None
gdal.Unlink(vsipath)

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.rlp_stream_rast_testarea_50x50;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.close()
conn.close()

numNLMs = 10
fac = 25

for x in range(numNLMs):
    
    print(x)

    nlm_R = nlmpy.random(int(nROW), int(nCOL))
    nlm_R = ((nlmpy.classifyArray(nlm_R, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_R)
    np.sum(nlm_R == 50)/(nROW * nCOL)
    np.sum(nlm_R == 75)/(nROW * nCOL)
    np.sum(nlm_R == 100)/(nROW * nCOL)
    
    np.place(nlm_R, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_R)
    np.sum(nlm_R == 25)/(nROW * nCOL)
    np.sum(nlm_R == 50)/(nROW * nCOL)
    np.sum(nlm_R == 75)/(nROW * nCOL)
    np.sum(nlm_R == 100)/(nROW * nCOL)

    #####

    nlm_RE = nlmpy.randomElementNN(int(nROW), int(nCOL), 1000*fac)
    nlm_RE = ((nlmpy.classifyArray(nlm_RE, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_RE)
    np.sum(nlm_RE == 50)/(nROW * nCOL)
    np.sum(nlm_RE == 75)/(nROW * nCOL)
    np.sum(nlm_RE == 100)/(nROW * nCOL)
    
    np.place(nlm_RE, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_RE)
    np.sum(nlm_RE == 25)/(nROW * nCOL)
    np.sum(nlm_RE == 50)/(nROW * nCOL)
    np.sum(nlm_RE == 75)/(nROW * nCOL)
    np.sum(nlm_RE == 100)/(nROW * nCOL)
    
    #####
    
    nlm_RC = nlmpy.randomClusterNN(int(nROW), int(nCOL), .3825, n = '8-neighbourhood')
    nlm_RC = ((nlmpy.classifyArray(nlm_RC, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_RC)
    np.sum(nlm_RC == 50)/(nROW * nCOL)
    np.sum(nlm_RC == 75)/(nROW * nCOL)
    np.sum(nlm_RC == 100)/(nROW * nCOL)
    
    np.place(nlm_RC, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_RC)
    np.sum(nlm_RC == 25)/(nROW * nCOL)
    np.sum(nlm_RC == 50)/(nROW * nCOL)
    np.sum(nlm_RC == 75)/(nROW * nCOL)
    np.sum(nlm_RC == 100)/(nROW * nCOL)

    #####

    dst_filename = '/.../.../pY_rASTER/nlm_R.tiff'

    wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    
    driver = gdal.GetDriverByName('GTiff')
    
    dataset=[]
    
    dataset = driver.Create(
        dst_filename,
        int(nCOL),
        int(nROW),
        1,
        gdal.GDT_Float32)
    
    dataset.SetGeoTransform((
        X_ll, 
        cellSIZE, 
        0,                    
        Y_ll,
        0,
        -cellSIZE))
    
    dataset.FlushCache()  # Write to disk.
    
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(nlm_R)
    
    dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_R), np.amax(nlm_R), np.mean(nlm_R), np.std(nlm_R))
    dataset.GetRasterBand(1).SetNoDataValue(-999)
    
    print(dataset.GetRasterBand(1).ReadAsArray())
    
    dataset.FlushCache()  # Write to disk.
    
    raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)
    
    raster_array = raster.ReadAsArray()
    
    print raster_array

    conn = psycopg2.connect("host=localhost port=5432 dbname=??? user=??? password=???")

    cursor = conn.cursor()
    
    os.environ['PGPASSWORD'] = '???'

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmr_testarea_50x50_'+str(x)+' | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmr_testarea_50x50_'+str(x)+'_resamp | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)

    #####

    dst_filename = '/.../.../pY_rASTER/nlm_Rc.tiff'

    wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    
    driver = gdal.GetDriverByName('GTiff')
    
    dataset=[]
    
    dataset = driver.Create(
        dst_filename,
        int(nCOL),
        int(nROW),
        1,
        gdal.GDT_Float32)
    
    dataset.SetGeoTransform((
        X_ll, 
        cellSIZE, 
        0,                    
        Y_ll,
        0,
        -cellSIZE))
    
    dataset.FlushCache()  # Write to disk.
    
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(nlm_RC)
    
    dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RC), np.amax(nlm_RC), np.mean(nlm_RC), np.std(nlm_RC))
    dataset.GetRasterBand(1).SetNoDataValue(-999)
    
    print(dataset.GetRasterBand(1).ReadAsArray())
    
    dataset.FlushCache()  # Write to disk.
    
    raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)
    
    raster_array = raster.ReadAsArray()
    
    print raster_array

    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()

    os.environ['PGPASSWORD'] = '???'

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmrc_testarea_50x50_'+str(x)+' | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmrc_testarea_50x50_'+str(x)+'_resamp | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)

    #####

    dst_filename = '/.../.../pY_rASTER/nlm_RE.tiff'

    wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    
    driver = gdal.GetDriverByName('GTiff')
    
    dataset=[]
    
    dataset = driver.Create(
        dst_filename,
        int(nCOL),
        int(nROW),
        1,
        gdal.GDT_Float32)
    
    dataset.SetGeoTransform((
        X_ll, 
        cellSIZE, 
        0,                    
        Y_ll,
        0,
        -cellSIZE))
    
    dataset.FlushCache()  # Write to disk.
    
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(nlm_RE)
    
    dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RE), np.amax(nlm_RE), np.mean(nlm_RE), np.std(nlm_RE))
    dataset.GetRasterBand(1).SetNoDataValue(-999)
    
    print(dataset.GetRasterBand(1).ReadAsArray())
    
    dataset.FlushCache()  # Write to disk.
    
    raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)
    
    raster_array = raster.ReadAsArray()
    
    print raster_array

    conn = psycopg2.connect("host=localhost port=5432 dbname=??? user=??? password=???")
    cursor = conn.cursor()

    os.environ['PGPASSWORD'] = '???'

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmre_testarea_50x50_'+str(x)+' | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmre_testarea_50x50_'+str(x)+'_resamp | psql -d ??? -h ??? -U ??? '
    subprocess.call(cmds, shell=True)
