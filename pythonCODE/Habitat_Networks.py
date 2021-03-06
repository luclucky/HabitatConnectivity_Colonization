
import numpy as np
np.set_printoptions(suppress=True)

import gdal

import psycopg2

from skimage.graph import route_through_array

import multiprocessing 
from multiprocessing import Pool

def costRASTER_shortPATHs(inSCHEMA):
        
    def ind_to_Xcoord(ind_x):
        
        coord_x = ind_x * cr_gt[1] + cr_gt[0] + cr_gt[1]/2

        return(coord_x)
        
    def ind_to_Ycoord(ind_y):
        
        coord_y = ind_y * cr_gt[5] + cr_gt[3] + cr_gt[5]/2

        return(coord_y)
        
    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()
    
    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """+str(inSCHEMA)+""";""")
    conn.commit()

    numRandPTs = 10
    
    cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")
     
    ids = cursor.fetchall()
    ids = [i[0] for i in ids]
    
    for x in ids:
        
        for xx in range(numRandPTs):

            cursor.execute("""SELECT start, start_xy, aim, aim_xy, distance FROM dis_pts_2500_10x10_linear_01.dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""";""")
            
            dist_pts_2500 = cursor.fetchall()
            
            dist_pts_2500 = [list(y) for y in dist_pts_2500]
            
            dist_pts_2500 = [[y[0],[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])],y[2],[float(y[3].split(' ',1)[0][6:]), float(y[3].split(' ',1)[1][:-1])], y[4]] for y in dist_pts_2500]
            
            doub = [[y[2], y[0]]for y in dist_pts_2500],[[y[0], y[2]]for y in dist_pts_2500]
              
            dist_pts_2500_red = dist_pts_2500
               
            for xxx in range(len(doub[0])/2):
                    
                y = doub[0][xxx]
                    
                for xx in range(len(doub[0])):

                    yy = doub[1][xx]
                
                    if yy == y:
                        
                        doub[0].pop(xx)
                        doub[1].pop(xx)
                        dist_pts_2500_red.pop(xx)
                        break
            
            numNLMs = 10
        
            for xxxx in range(numNLMs):
                                                            
                cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM """+str(inSCHEMA[:-10])+"""_random_01.nlmr_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+""";""")
                
                vsipath = '/vsimem/from_postgis'
                
                gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
                
                cost_raster = gdal.Open(vsipath)
                
                gdal.Unlink(vsipath)
                
                cr_array = cost_raster.ReadAsArray()

                cr_gt = cost_raster.GetGeoTransform()

                cursor.execute("""DROP TABLE IF EXISTS """+str(inSCHEMA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""";""")

                cursor.execute("""CREATE TABLE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start bigint, aim bigint, geom geometry, costs double precision);""")
                
                for xxxxx in range(len(dist_pts_2500_red)):
                
                    start_x = int((dist_pts_2500_red[xxxxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    start_y = int((dist_pts_2500_red[xxxxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    aim_x = int((dist_pts_2500_red[xxxxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    aim_y = int((dist_pts_2500_red[xxxxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
                
                    indices = np.array(indices).T
                    
                    coordinates = []
                    
                    mPTs = ""
                    
                    for xxxxxx in range(len(indices[0])):
                    
                        coordinates.append([ind_to_Xcoord(indices[0][xxxxxx]), ind_to_Ycoord(indices[1][xxxxxx])])
                
                        mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxxxx][0]) + ', ' + str(coordinates[xxxxxx][1])+"),"
                
                    mPTs = mPTs[:-1]
        
                    cursor.execute("""INSERT INTO """+str(inSCHEMA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxxxx][0])+""", """+str(dist_pts_2500_red[xxxxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 
                    
                    cursor.execute("""UPDATE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" SET costs = 50 WHERE costs = 0;""")
        
                    conn.commit()
        
        ###
        
            for xxxx in range(numNLMs):
                                                            
                cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM """+str(inSCHEMA[:-10])+"""_random_01.nlmrc_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+""";""")
                
                vsipath = '/vsimem/from_postgis'
                
                gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
                
                cost_raster = gdal.Open(vsipath)
                
                gdal.Unlink(vsipath)
                
                cr_array = cost_raster.ReadAsArray()

                cr_gt = cost_raster.GetGeoTransform()

                cursor.execute("""DROP TABLE IF EXISTS """+str(inSCHEMA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""";""")

                cursor.execute("""CREATE TABLE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start bigint, aim bigint, geom geometry, costs double precision);""")
                
                for xxxxx in range(len(dist_pts_2500_red)):
                
                    start_x = int((dist_pts_2500_red[xxxxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    start_y = int((dist_pts_2500_red[xxxxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    aim_x = int((dist_pts_2500_red[xxxxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    aim_y = int((dist_pts_2500_red[xxxxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)

                    indices = np.array(indices).T
                    
                    coordinates = []
                    
                    mPTs = ""
                    
                    for xxxxxx in range(len(indices[0])):
                    
                        coordinates.append([ind_to_Xcoord(indices[0][xxxxxx]), ind_to_Ycoord(indices[1][xxxxxx])])
                
                        mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxxxx][0]) + ', ' + str(coordinates[xxxxxx][1])+"),"
                
                    mPTs = mPTs[:-1]
        
                    cursor.execute("""INSERT INTO """+str(inSCHEMA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxxxx][0])+""", """+str(dist_pts_2500_red[xxxxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 
                    
                    cursor.execute("""UPDATE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" SET costs = 50 WHERE costs = 0;""")
        
                    conn.commit()
        
        #####
        
            for xxxx in range(numNLMs):

                cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM """+str(inSCHEMA[:-10])+"""_random_01.nlmre_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+""";""")
                
                vsipath = '/vsimem/from_postgis'
                
                gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
                
                cost_raster = gdal.Open(vsipath)
                
                gdal.Unlink(vsipath)
                
                cr_array = cost_raster.ReadAsArray()

                cr_gt = cost_raster.GetGeoTransform()

                cursor.execute("""DROP TABLE IF EXISTS """+str(inSCHEMA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""";""")
        
                cursor.execute("""CREATE TABLE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start bigint, aim bigint, geom geometry, costs double precision);""")
                
                for xxxxx in range(len(dist_pts_2500_red)):
                
                    start_x = int((dist_pts_2500_red[xxxxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    start_y = int((dist_pts_2500_red[xxxxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    aim_x = int((dist_pts_2500_red[xxxxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
                    aim_y = int((dist_pts_2500_red[xxxxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
                    
                    indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)

                    indices = np.array(indices).T
                    
                    coordinates = []
                    
                    mPTs = ""
                    
                    for xxxxxx in range(len(indices[0])):
                    
                        coordinates.append([ind_to_Xcoord(indices[0][xxxxxx]), ind_to_Ycoord(indices[1][xxxxxx])])
                
                        mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxxxx][0]) + ', ' + str(coordinates[xxxxxx][1])+"),"
                
                    mPTs = mPTs[:-1]
        
                    cursor.execute("""INSERT INTO """+str(inSCHEMA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxxxx][0])+""", """+str(dist_pts_2500_red[xxxxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 
        
                    cursor.execute("""UPDATE """+str(inSCHEMA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(xxxx)+"""_"""+str(x)+"""_start_"""+str(xx)+""" SET costs = 50 WHERE costs = 0;""")
        
                    conn.commit()

    cursor.close()
    conn.close()

def main():

    inSCHEMAs = ['stream_network_000050050_linear_01', 'stream_network_025375375_linear_01', 'stream_network_075125125_linear_01', 'stream_network_100000000_linear_01', 'stream_network_050000050_linear_01','stream_network_375025375_linear_01', 'stream_network_125075125_linear_01', 'stream_network_000100000_linear_01', 'stream_network_050050000_linear_01', 'stream_network_375375025_linear_01','stream_network_125125075_linear_01', 'stream_network_000000100_linear_01', 'stream_network_050025025_linear_01', 'stream_network_025050025_linear_01', 'stream_network_025025050_linear_01']

    pool = multiprocessing.Pool(processes=12)
    pool.map(costRASTER_shortPATHs, inSCHEMAs)

    pool.close()
    pool.join()
    
if __name__ == '__main__':
    
    main()
