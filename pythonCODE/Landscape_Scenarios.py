import numpy as np

np.set_printoptions(suppress=True)

import gdal, os

import psycopg2

import subprocess

import nlmpy

import re

import warnings

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

#####

# Query of Raster MetaData

cursor.execute("""SELECT ST_MetaData(rast) As md FROM stream_network.rlp_stream_rast_testarea_50x50;""")
raster_MD = cursor.fetchall()
raster_MD = [float(xx) for xx in raster_MD[0][0][1:-1].split(',')]

# Query Dimensions of Raster-Matrix & Cell-Size

nCOL = raster_MD[2]
nROW = raster_MD[3]
grid = np.zeros((nCOL, nROW))

X_DIM = np.arange(grid.shape[0])
Y_DIM = np.arange(grid.shape[1])

X_ll = raster_MD[0]
Y_ll = raster_MD[1]

cellSIZE = raster_MD[4]

vsipath = '/vsimem/from_postgis'

cursor.execute("""SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';""")

ds = band = None
gdal.Unlink(vsipath)

# ???

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.rlp_stream_rast_testarea_50x50;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.close()
conn.close()

### Variables definition

# Number of NLMs produced

numNLMs = 10

# Shares of Landscape-Types 1-3

share_LT = [[[1], 25], [[.75, .125, .125], 25], [[.5, .25, .25], 25], [[.25, .375, .375], 25], [[.5, .5], 50],[[1], 50], [[.125, .75, .125], 25], [[.25, .5, .25], 25], [[.375, .25, .375], 25], [[.5, 0, .5], 25], [[1], 75], [[.125, .125, .75], 25], [[.25, .25, .5], 25], [[.375, .375, .25], 25], [[.5, .5, 0], 25]]

# Naming Schema

schemaNAME = ['100000000', '075125125', '050025025', '025375375', '000050050', '000100000', '125075125', '025050025', '375025375', '050000050', '000000100', '125125075', '025025050', '375375025', '050050000']

# OpenGIS Well Known Text description of coordinate system used

wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

for x in range(share_LT):

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS stream_network_""" + str(schemaNAME[x]) + """;""")
    conn.commit()

    for xx in range(numNLMs):

        ### NLMs see https://besjournals.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2F2041-210X.12308&file=mee312308-sup-0001-dataS1.pdf

        # random NLM

        nlm_R = nlmpy.random(int(nROW), int(nCOL))
        nlm_R = ((nlmpy.classifyArray(nlm_R, share_LT[x][0]) + 1) * 25) + share_LT[x][1]

        # random element NLM

        nlm_RE = nlmpy.randomElementNN(int(nROW), int(nCOL), 1000 * 25)
        nlm_RE = ((nlmpy.classifyArray(nlm_RE, share_LT[x][0]) + 1) * 25) + share_LT[x][1]

        # random cluster NLM

        nlm_RC = nlmpy.randomClusterNN(int(nROW), int(nCOL), .3825, n='8-neighbourhood')
        nlm_RC = ((nlmpy.classifyArray(nlm_RC, share_LT[x][0]) + 1) * 25) + share_LT[x][1]

        ###

        dst_filename = '/.../.../pY_rASTER/nlm_R.tiff'

        driver = gdal.GetDriverByName('GTiff')

        dataset = []

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

        dataset.FlushCache()  # Write to disk.

### Import to Database

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")

        cursor = conn.cursor()

        os.environ['PGPASSWORD'] = '???'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_' + str(schemaNAME[x]) + '.nlmr_testarea_50x50_' + str(xx) + ' | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
        subprocess.call(cmds, shell=True)

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_' + str(schemaNAME[x]) + '.nlmr_testarea_50x50_' + str(xx) + '_resamp | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

        #####

        dst_filename = '/.../.../pY_rASTER/nlm_Rc.tiff'

        driver = gdal.GetDriverByName('GTiff')

        dataset = []

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

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        print raster_array

        conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
        cursor = conn.cursor()

        os.environ['PGPASSWORD'] = '???'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_' + str(schemaNAME[x]) + '.nlmrc_testarea_50x50_' + str(xx) + ' | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
        subprocess.call(cmds, shell=True)

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_' + str(schemaNAME[x]) + '.nlmrc_testarea_50x50_' + str(xx) + '_resamp | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

        #####

        dst_filename = '/.../.../pY_rASTER/nlm_RE.tiff'

        driver = gdal.GetDriverByName('GTiff')

        dataset = []

        dataset = driver.Create(dst_filename,
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

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        print raster_array

        conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
        cursor = conn.cursor()

        os.environ['PGPASSWORD'] = '???'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_' + str(schemaNAME[x]) + '.nlmre_testarea_50x50_' + str(xx) + ' | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
        subprocess.call(cmds, shell=True)

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_' + str(schemaNAME[x]) + '.nlmre_testarea_50x50_' + str(xx) + '_resamp | psql -d ??? -h ??? -U ??? '
        subprocess.call(cmds, shell=True)

#####

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")

cursor = conn.cursor()

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:

    print(x)

    cursor.execute("""SELECT ST_Extent(geom) FROM stream_network.rast_10x10 WHERE ids = """ + str(x) + """;""")
    ext = cursor.fetchone()
    ext = re.findall(r"[\w.]+", ext[0])[1:]
    ext = [float(i) for i in ext]

    for xx in range(10):
        cursor.execute("""CREATE TABLE stream_network_625125025.nlmr_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope(""" + str(ext)[1:-1] + """), 25832))) AS rast FROM stream_network_625125025.nlmr_testarea_50x50_""" + str(xx) + """_resamp;""")

        cursor.execute("""SELECT addrasterconstraints('stream_network_625125025'::name, 'nlmr_testarea_50x50_""" + str(xx) + """_""" + str(x) + """'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmr_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ SET rast = ST_SetSRID(rast,25832);""")

        ###

        cursor.execute("""CREATE TABLE stream_network_625125025.nlmrc_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope(""" + str(ext)[1:-1] + """), 25832))) AS rast FROM stream_network_625125025.nlmrc_testarea_50x50_""" + str(xx) + """_resamp;""")

        cursor.execute("""SELECT AddRasterConstraints('stream_network_625125025'::name, 'nlmrc_testarea_50x50_""" + str(xx) + """_""" + str(x) + """'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmrc_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ SET rast = ST_SetSRID(rast,25832);""")

        ###

        cursor.execute("""CREATE TABLE stream_network_625125025.nlmre_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope(""" + str(ext)[1:-1] + """), 25832))) AS rast FROM stream_network_625125025.nlmre_testarea_50x50_""" + str(xx) + """_resamp;""")

        cursor.execute("""SELECT AddRasterConstraints('stream_network_625125025'::name, 'nlmre_testarea_50x50_""" + str(xx) + """_""" + str(x) + """'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmre_testarea_50x50_""" + str(xx) + """_""" + str(x) + """ SET rast = ST_SetSRID(rast,25832);""")

conn.commit()

cursor.close()
conn.close()
