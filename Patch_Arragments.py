
import numpy as np

import random

import psycopg2

import re

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

def randomSAMPLE(randHAPTS_IDS, maxHABs):
    
    random_SAMPLE = random.sample(randHAPTS_IDS, maxHABs)

    return(random_SAMPLE)

def randomSAMPLE_CLUSTER(nrCLU, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs):

    randHAPTS_IDS_samp = [y for y in randHAPTS_IDS if y not in startHABs]
    
    coord_IDS = random.sample((randHAPTS_IDS_samp), nrCLU-len(startHABs)) + startHABs

    coord_CLUSTERsCENTER = np.array([[randHAPTS_X[randHAPTS_IDS.index(y)],randHAPTS_Y[randHAPTS_IDS.index(y)]] for y in coord_IDS]) 

    randHAPTS_IDS_CLUSTER = np.array([], int)

    for x in range(len(coord_CLUSTERsCENTER)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_CLUSTERsCENTER[x][0])**2 + (randHAPTS_Y - coord_CLUSTERsCENTER[x][1])**2))
    
        randHAPTS_IDS_CLUSTER = np.append(randHAPTS_IDS_CLUSTER, np.array(randHAPTS_IDS)[np.where(dist < RADIUS)[0]])
    
    randHAPTS_IDS_CLUSTER = np.unique(randHAPTS_IDS_CLUSTER.flatten())

    randHAPTS_IDS_CLUSTER = [y for y in randHAPTS_IDS_CLUSTER if y not in coord_IDS]

    if (maxHABs != None and len(randHAPTS_IDS_CLUSTER) > maxHABs- len(coord_IDS)):
        
        randHAPTS_IDS_CLUSTER = random.sample(randHAPTS_IDS_CLUSTER, maxHABs - len(coord_IDS))

        randHAPTS_IDS_CLUSTER = randHAPTS_IDS_CLUSTER + coord_IDS

        return (randHAPTS_IDS_CLUSTER)
        
    else:

        randomSAMPLE_CLUSTER(nrCLU, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs)

def randomSAMPLE_LINEAR(nrLIN, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs):
    
    randHAPTS_IDS_samp = [y for y in randHAPTS_IDS if y not in startHABs]
    
    coord_LINEsCENTER_IDs = random.sample((randHAPTS_IDS_samp), nrLIN-len(startHABs)) + startHABs
    
    coord_LINEsCENTER_XY = np.array([[randHAPTS_X[randHAPTS_IDS.index(y)],randHAPTS_Y[randHAPTS_IDS.index(y)]] for y in coord_LINEsCENTER_IDs]) 
    
    randHAPTS_IDS_LINEs = np.array([], int)
        
    for x in range(len(coord_LINEsCENTER_IDs)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_LINEsCENTER_XY[x][0])**2 + (randHAPTS_Y - coord_LINEsCENTER_XY[x][1])**2))
    
        randHAPTS_IDS_LINE = np.array(randHAPTS_IDS)[np.where(dist < np.random.choice(range(int(RADIUS - RADIUS * .1) , int(RADIUS + RADIUS * .1))))[0]]

        randHAPTS_IDS_LINEs = np.append(randHAPTS_IDS_LINEs, randHAPTS_IDS_LINE)
    
    randHAPTS_IDS_LINEs = np.unique(randHAPTS_IDS_LINEs.flatten())

    randHAPTS_IDS_LINEs = [y for y in randHAPTS_IDS_LINEs if y not in coord_LINEsCENTER_IDs]

    if (maxHABs != None and len(randHAPTS_IDS_LINEs) > maxHABs - len(coord_LINEsCENTER_IDs)):

        randHAPTS_IDS_LINEs = random.sample(randHAPTS_IDS_LINEs, (maxHABs - len(coord_LINEsCENTER_IDs)))

        randHAPTS_IDS_LINEs = randHAPTS_IDS_LINEs + coord_LINEsCENTER_IDs

        return (randHAPTS_IDS_LINEs)

    else:

        randomSAMPLE_LINEAR(nrLIN, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs)

numRandPTs = 10

patcSHARs = [0.1,0.2]

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")
 
ids = cursor.fetchall()
ids = [y[0] for y in ids]

for patcSHAR in patcSHARs:

    SHR = str(patcSHAR).replace('.', '')

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS dis_pts_2500_10x10_random_"""+str(SHR)+""";""")
    cursor.execute("""CREATE SCHEMA IF NOT EXISTS dis_pts_2500_10x10_clustr_"""+str(SHR)+""";""")
    cursor.execute("""CREATE SCHEMA IF NOT EXISTS dis_pts_2500_10x10_linear_"""+str(SHR)+""";""")
    conn.commit()

    for x in ids:

        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(x)+""";""")
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(x)+""";""")

        conn.commit()

        cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""";""")

        randHAPTS =  cursor.fetchall()

        randHAPTS = [list(y) for y in randHAPTS]

        randHAPTS = [[int(y[0]),[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])]] for y in randHAPTS]

        randHAPTS_IDS = [int(y[0]) for y in randHAPTS]
        randHAPTS_X = [float(y[1][0]) for y in randHAPTS]
        randHAPTS_Y = [float(y[1][1]) for y in randHAPTS]
        randHAPTS_XY = [y[1] for y in randHAPTS]

        for xx in range(numRandPTs):

            PTs_rSa = randomSAMPLE(randHAPTS_IDS, int(len(randHAPTS_IDS)*patcSHAR+0.5))

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" WHERE ids IN ("""+str(PTs_rSa)[1:-1]+""");""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" RENAME COLUMN ids TO ids_org;""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" ADD column ids bigserial;""")

            conn.commit()

            cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""";""")

            ids = cursor.fetchall()
            ids = [int(y[0]) for y in ids]

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET start = (SELECT dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".start = dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET aim = (SELECT dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_random_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".aim = dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            conn.commit()

    ### StartHABs

    inHABs = []

    for x in range(25):

        inHABs.append('pts_habitat_red_'+str(x+1))

    for inHAB in inHABs:

        for xx in range(10):

            cursor.execute("""SELECT idS, st_astext(geom) FROM dis_pts_2500_10x10_random_"""+str(SHR)+"""."""+str(inHAB)+"""_start_"""+str(xx)+""";""")
            xy_pts = cursor.fetchall()
            xy_pts = [[y[0],re.findall(r"[\w']+",y[1])[1:]] for y in xy_pts]
            xy_pts = [[y[0], float(y[1][0]), float(y[1][2])] for y in xy_pts]
            xy_pts.sort()

            hab_id = [int(s[0]) for s in xy_pts]
            list_SH = []

            for s in range(10):

                list_SH.append(np.random.choice(hab_id, int(len(hab_id)*0.1+0.5), replace = False).astype(int)) # number of occupied habitats first run

        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_"""+str(SHR)+"""."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+"""."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+"""."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")

        toINS_list_SH = np.array(list_SH).T
        toINS_list_SH = toINS_list_SH.tolist()
        toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')

        cursor.execute("""INSERT INTO dis_pts_2500_10x10_random_"""+str(SHR)+"""."""+str(inHAB)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")

        conn.commit()

    ### Random around centers

    cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")

    ids = cursor.fetchall()
    ids = [y[0] for y in ids]

    for x in ids:

        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(x)+""";""")
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(x)+""";""")

        conn.commit()

        cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""";""")
        randHAPTS =  cursor.fetchall()
        randHAPTS = [list(y) for y in randHAPTS]
        randHAPTS = [[int(y[0]),[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])]] for y in randHAPTS]

        randHAPTS_IDS = [int(y[0]) for y in randHAPTS]
        randHAPTS_X = [float(y[1][0]) for y in randHAPTS]
        randHAPTS_Y = [float(y[1][1]) for y in randHAPTS]
        randHAPTS_XY = [y[1] for y in randHAPTS]

        cursor.execute("""SELECT * FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_starthabitas;""")
        LIST_startHABs = cursor.fetchall()
        LIST_startHABs = np.array(LIST_startHABs).T

        toINS_list_SH = []

        for xx in range(numRandPTs):

            cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE ids IN ("""+str(LIST_startHABs[xx].tolist())[1:-1].replace('L','')+""");""")
            startHABs = cursor.fetchall()
            startHABs = [int(y[0]) for y in startHABs]

            PTs_rCl = randomSAMPLE_CLUSTER(int(len(randHAPTS_IDS)*0.05+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*patcSHAR+0.5))

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" WHERE ids IN ("""+str(PTs_rCl)[1:-1]+""");""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" RENAME COLUMN ids TO ids_org;""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" ADD column ids bigserial;""")

            cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE ids_org IN ("""+str(startHABs)[1:-1]+""");""")
            toINS = cursor.fetchall()
            toINS = [int(y[0]) for y in toINS]

            toINS_list_SH.append(toINS)

            conn.commit()

            cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""";""")

            ids = cursor.fetchall()
            ids = [int(y[0]) for y in ids]

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET start = (SELECT dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".start = dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET aim = (SELECT dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_clustr_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".aim = dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            conn.commit()

        toINS_list_SH = np.array(toINS_list_SH).T
        toINS_list_SH = toINS_list_SH.tolist()
        toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')

        cursor.execute("""INSERT INTO dis_pts_2500_10x10_clustr_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")

        conn.commit()

    cursor.close()
    conn.close()

    ### Contiguous around centers

    numRandPTs = 10

    cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")

    ids = cursor.fetchall()
    ids = [y[0] for y in ids]

    for x in ids:

        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(x)+""";""")
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(x)+""";""")

        conn.commit()

        cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""";""")
        randHAPTS =  cursor.fetchall()
        randHAPTS = [list(y) for y in randHAPTS]
        randHAPTS = [[int(y[0]),[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])]] for y in randHAPTS]

        randHAPTS_IDS = [int(y[0]) for y in randHAPTS]
        randHAPTS_X = [float(y[1][0]) for y in randHAPTS]
        randHAPTS_Y = [float(y[1][1]) for y in randHAPTS]
        randHAPTS_XY = [y[1] for y in randHAPTS]

        cursor.execute("""SELECT * FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_starthabitas;""")
        LIST_startHABs = cursor.fetchall()
        LIST_startHABs = np.array(LIST_startHABs).T

        toINS_list_SH = []

        for xx in range(numRandPTs):

            cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE ids IN ("""+str(LIST_startHABs[xx].tolist())[1:-1].replace('L','')+""");""")
            startHABs = cursor.fetchall()
            startHABs = [int(y[0]) for y in startHABs]

            PTs_rLi = randomSAMPLE_LINEAR(int(len(randHAPTS_IDS)*0.025+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*patcSHAR+0.5))

            if (len(PTs_rLi) < int(len(randHAPTS_IDS)*patcSHAR+0.5)):
                PTs_rLi = randomSAMPLE_LINEAR(int(len(randHAPTS_IDS)*0.025+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*patcSHAR+0.5))

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+""" WHERE ids IN ("""+str(PTs_rLi)[1:-1]+""");""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" RENAME COLUMN ids TO ids_org;""")

            cursor.execute("""ALTER TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" ADD column ids bigserial;""")


            cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE ids_org IN ("""+str(startHABs)[1:-1]+""");""")
            toINS = cursor.fetchall()
            toINS = [int(y[0]) for y in toINS]

            toINS_list_SH.append(toINS)

            conn.commit()

            cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""";""")

            ids = cursor.fetchall()
            ids = [int(y[0]) for y in ids]

            cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET start = (SELECT dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".start = dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            cursor.execute("""UPDATE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""" SET aim = (SELECT dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids FROM dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""" WHERE dis_pts_2500_10x10_linear_"""+str(SHR)+""".dist_pts_2500_"""+(str(x))+"""_start_"""+str(xx)+""".aim = dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_start_"""+str(xx)+""".ids_org);""")

            conn.commit()

        toINS_list_SH = np.array(toINS_list_SH).T
        toINS_list_SH = toINS_list_SH.tolist()
        toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')

        cursor.execute("""INSERT INTO dis_pts_2500_10x10_linear_"""+str(SHR)+""".pts_habitat_red_"""+str(x)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")

        conn.commit()

cursor.close()
conn.close()
