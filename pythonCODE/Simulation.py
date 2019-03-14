
import numpy as np
np.set_printoptions(suppress=True)

import psycopg2

import re

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

import multiprocessing 
from multiprocessing import Pool

def PROBreachCONHABITAT(Co, maxCo):
    
    P = Co * 0.0

    P[np.where(Co < maxCo)] = (1 - (Co[np.where(Co < maxCo)] / maxCo))**2

    return P

def logGRO(K, N, r, t):
    
    Nt = (K * N) / (N + (K - N) * np.exp(-r*t))

    return Nt

def DENdepEMI_RATE(M, N, K, s):

    EmRa = N * M * (N / (K)) **(s+1)

    return EmRa

def percDISTRI_INDIdisper(COSTs):

    CO_rev = ((COSTs-max(COSTs))*-1+min(COSTs))

    percIND = np.round(CO_rev**3/sum(CO_rev**3),2)

    return percIND            

#####

timesteps = 100
maxCo = 1250

igr = 2.0
t  = 1.0
     
m_max = 0.20
s = 0.5

extPROB_perRUN = 0.05
    
#####

def dispersal_MODEL(inPARA):
    
    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()
        
    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """+str(inPARA[2])+""";""")
    conn.commit()
    
    cursor.execute("""SELECT tablename FROM pg_tables WHERE schemaname = '"""+str(inPARA[2])+"""';""")
    procTABs = cursor.fetchall()

    procTABs = [y[0] for y in procTABs]

    inHABs = []

    for x in range(25):

        inHABs.append('pts_habitat_red_'+str(x+1))

    for inHAB in inHABs:
            
        for xx in range(10):

            cursor.execute("""SELECT idS, st_astext(geom) FROM dis_pts_2500_10x10_"""+str(inPARA[1][-9:])+"""."""+str(inHAB)+"""_start_"""+str(xx)+""";""")
            xy_pts = cursor.fetchall()
            xy_pts = [[y[0],re.findall(r"[\w']+",y[1])[1:]] for y in xy_pts]
            xy_pts = [[y[0], float(y[1][0]), float(y[1][2])] for y in xy_pts]
            xy_pts.sort()
            
            cursor.execute("""SELECT * FROM dis_pts_2500_10x10_"""+str(inPARA[1][-9:])+"""."""+str(inHAB)+"""_starthabitas;""")
            list_SH = cursor.fetchall()
            list_SH = np.array(list_SH).T

            for xxx in range(10):
        
                cursor.execute("""SELECT start, aim, costs FROM """+str(inPARA[1])+"""."""+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+""";""")
                habitats_shortpath_red = cursor.fetchall()
                habitats_shortpath_red = [y for y in habitats_shortpath_red if y[2] <= maxCo]
                habitats_shortpath_red = np.array(habitats_shortpath_red, dtype=object).T

                habitats_qual = np.array(len(xy_pts) * [0.625])

                if str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx) in procTABs:
                    continue
                
                cursor.execute("""CREATE TABLE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+""" (pts_id BIGINT, geom GEOMETRY, hq FLOAT);""")
                
                toINS_pts = np.array(xy_pts)
                toINS_pts = toINS_pts.tolist()
                 
                for y in range(len(toINS_pts)):
                
                    toINS_pts[y][1] = 'ST_SetSRID(ST_MakePoint' + str(toINS_pts[y][1:]).replace('[','(').replace(']',')')+', 25832)'
                    toINS_pts[y][2] = str(habitats_qual[y])
                
                toINS_pts = str(np.array(toINS_pts).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
                
                cursor.execute("""INSERT INTO """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+""" (pts_id, geom, hq) values """+toINS_pts+""";""")
                
                conn.commit()
                
                for xxxx in range(10):
                    
                    print(str(inPARA[1])+""": """+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+ ': run ' + str(xxxx))
                        
                    cursor.execute("""ALTER TABLE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+""" ADD firstcol_"""+str(xxxx+1)+""" bigint, ADD origin_"""+str(xxxx+1)+""" bigint, ADD biomass_"""+str(xxxx+1)+""" float, ADD first20_"""+str(xxxx+1)+""" bigint;""")

                    starthabitats = list_SH[xxxx]
                    
                    starthabitats_hq = habitats_qual[starthabitats-1]
                
                    occhabitats = np.array([range(len(habitats_qual)+1)[1:], [-999] * len(habitats_qual), [-999] * len(habitats_qual), [0.0] * len(habitats_qual), [-999] * len(habitats_qual)], dtype = object)
                                
                    occhabitats[1][(starthabitats-1).tolist()] = 0
                    occhabitats[2][(starthabitats-1).tolist()] = 0
                    occhabitats[3][(starthabitats-1).tolist()] = starthabitats_hq * 100.0
                    occhabitats[4][(starthabitats-1).tolist()] = 0
                
                    prob = PROBreachCONHABITAT(Co = habitats_shortpath_red[2], maxCo = maxCo)
                
                    for xxxxx in range(timesteps):
                                
                        if len(occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)) == 0:
                            break
                        
                        starthabitats = occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)

                        starthabitats_hq = habitats_qual[starthabitats-1] # habitat-quality of starthabitats
                        starthabitats_indnr = occhabitats[3][starthabitats-1] # number of individuals in starthabitats

                        starthabitats_indnr = logGRO(K = starthabitats_hq*100, N = starthabitats_indnr, r = igr, t = 1)
                            
                        occhabitats[3][starthabitats-1] = np.round(starthabitats_indnr.astype(float), 3)

                        starthabitats = starthabitats[np.where(occhabitats[3][starthabitats-1] >= 20)] # starthabitats with less than 20 individuals are remove from starthabitats 
                
                        for xxxxxx in range(len(starthabitats)):
                
                            if starthabitats[xxxxxx] in habitats_shortpath_red[0] or starthabitats[xxxxxx] in habitats_shortpath_red[1]:
                                conhabitats_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == starthabitats[xxxxxx])[0].tolist(), np.where(habitats_shortpath_red[1] == starthabitats[xxxxxx])[0].tolist()]).flat).tolist()
                                
                                conhabitats_ind = [int(y) for y in conhabitats_ind]
                                
                            else:
                                continue
                                
                            torem = []
                
                            for y in conhabitats_ind:
                                
                                if habitats_shortpath_red[0][y] != starthabitats[xxxxxx]:
                                
                                    if occhabitats[3][habitats_shortpath_red[0][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[0][y]-1]-1]*100:
                                        
                                        torem.append(y)
                                
                                else:
                                    
                                    if occhabitats[3][habitats_shortpath_red[1][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[1][y]-1]-1]*100:
              
                                        torem.append(y)
                
                            for yy in torem:
                            
                                conhabitats_ind.remove(yy)   
                
                            if conhabitats_ind == []:
                            
                                continue
                            
                            disind = DENdepEMI_RATE(M = m_max, N = occhabitats[3][starthabitats[xxxxxx]-1], K = habitats_qual[starthabitats[xxxxxx]-1]*100, s = s)
                                   
                            occhabitats[3][starthabitats[xxxxxx]-1] = occhabitats[3][starthabitats[xxxxxx]-1] - disind
                    
                            disind_part = percDISTRI_INDIdisper(COSTs = habitats_shortpath_red[2][conhabitats_ind].astype(float))
                
                            for xxxxxxx in conhabitats_ind:
                                                
                                disind_perc = disind * disind_part[0]
                                
                                disind_part = disind_part[1:]

                                disind_perc = disind_perc * prob[xxxxxxx]
                                     
                                if disind_perc == 0.0:
                                    
                                    continue
                                            
                                if occhabitats[0][habitats_shortpath_red[0][xxxxxxx]-1] != starthabitats[xxxxxx]:
                                    
                                    if occhabitats[1][habitats_shortpath_red[0][xxxxxxx]-1] in (-111, -999):
                                    
                                        occhabitats[1][habitats_shortpath_red[0][xxxxxxx]-1] = xxxxx+1 # ts of first population of h
                                        
                                    if occhabitats[2][habitats_shortpath_red[0][xxxxxxx]-1] in (-111, -999):
                                        
                                        occhabitats[2][habitats_shortpath_red[0][xxxxxxx]-1] = starthabitats[xxxxxx] # h populated from which sh
                                                
                                    if occhabitats[3][habitats_shortpath_red[0][xxxxxxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[0][xxxxxxx]-1]-1]*100): # max pop size hq * 100
                                                                                   
                                        occhabitats[3][habitats_shortpath_red[0][xxxxxxx]-1] = occhabitats[3][habitats_shortpath_red[0][xxxxxxx]-1] + disind_perc # function to calculate number of individuals in h -> plus disind_perc
                                        
                                    if  occhabitats[4][habitats_shortpath_red[0][xxxxxxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[0][xxxxxxx]-1] >= 20.0:
                                        occhabitats[4][habitats_shortpath_red[0][xxxxxxx]-1] = xxxxx+1
                                        
                                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[0][xxxxxxx]-1]]), return_index=True)
                                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                                    
                                if occhabitats[0][habitats_shortpath_red[1][xxxxxxx]-1] != starthabitats[xxxxxx]:
                                       
                                    if occhabitats[1][habitats_shortpath_red[1][xxxxxxx]-1] in (-111, -999):
                                                                
                                        occhabitats[1][habitats_shortpath_red[1][xxxxxxx]-1] = xxxxx+1 # ts of first population of h
                                    
                                    if occhabitats[2][habitats_shortpath_red[1][xxxxxxx]-1] in (-111, -999):
                
                                        occhabitats[2][habitats_shortpath_red[1][xxxxxxx]-1] = starthabitats[xxxxxx] # h populated from which sh
                                    
                                    if occhabitats[3][habitats_shortpath_red[1][xxxxxxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[1][xxxxxxx]-1]-1]*100): # max pop size hq * 100
                
                                        occhabitats[3][habitats_shortpath_red[1][xxxxxxx]-1] = occhabitats[3][habitats_shortpath_red[1][xxxxxxx]-1] + disind_perc # function to calculate number of individuals in h -> plus disind_perc
                                  
                                    if  occhabitats[4][habitats_shortpath_red[1][xxxxxxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[1][xxxxxxx]-1] >= 25:
                                        occhabitats[4][habitats_shortpath_red[1][xxxxxxx]-1] = xxxxx+1
                                        
                                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[1][xxxxxxx]-1]]), return_index=True)
                                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                
                    occhabitats[3] = occhabitats[3] * 25.0 # conversion into mg biomass   
                          
                    toINS_DB = str(np.array(occhabitats).T.tolist())[1:-1].replace('[','(').replace(']',')')

                    cursor.execute("""UPDATE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(xxx)+"""_"""+str(inHAB[16:])+"""_start_"""+str(xx)+""" SET firstcol_"""+str(xxxx+1)+""" = firstcol_"""+str(xxxx+1)+"""_arr, origin_"""+str(xxxx+1)+"""xxxxxxx = origin_"""+str(xxxx+1)+"""_arr, biomass_"""+str(xxxx+1)+""" = biomass_"""+str(xxxx+1)+"""_arr, first20_"""+str(xxxx+1)+""" = first20_"""+str(xxxx+1)+"""_arr from (values """+toINS_DB+""") as c(pts_id_arr, firstcol_"""+str(xxxx+1)+"""_arr, origin_"""+str(xxxx+1)+"""_arr, biomass_"""+str(xxxx+1)+"""_arr, first20_"""+str(xxxx+1)+"""_arr) WHERE pts_id = pts_id_arr;""")
                
                conn.commit()

    cursor.close()
    conn.close()

#####

def main():

    inSCHEMAs = ['stream_network_000050050_linear_02', 'stream_network_025375375_linear_02', 'stream_network_075125125_linear_02', 'stream_network_100000000_linear_02', 'stream_network_050000050_linear_02','stream_network_375025375_linear_02', 'stream_network_125075125_linear_02', 'stream_network_000100000_linear_02', 'stream_network_050050000_linear_02', 'stream_network_375375025_linear_02','stream_network_125125075_linear_02', 'stream_network_000000100_linear_02', 'stream_network_050025025_linear_02', 'stream_network_025050025_linear_02', 'stream_network_025025050_linear_02']
    
    outSCHEMAs = ['stream_network_000050050_linear_02_results', 'stream_network_025375375_linear_02_results', 'stream_network_075125125_linear_02_results', 'stream_network_100000000_linear_02_results', 'stream_network_050000050_linear_02_results','stream_network_375025375_linear_02_results', 'stream_network_125075125_linear_02_results', 'stream_network_000100000_linear_02_results', 'stream_network_050050000_linear_02_results', 'stream_network_375375025_linear_02_results','stream_network_125125075_linear_02_results', 'stream_network_000000100_linear_02_results', 'stream_network_050025025_linear_02_results', 'stream_network_025050025_linear_02_results', 'stream_network_025025050_linear_02_results']
     
    inNLMs = ['habitats_shortpath_red_nlmr_testarea', 'habitats_shortpath_red_nlmrc_testarea', 'habitats_shortpath_red_nlmre_testarea']
    
    inPARAs = []
    
    for x in range(len(inNLMs)):
        
        for xx in range(len(inSCHEMAs)):
        
            inPARAs.append([inNLMs[x],inSCHEMAs[xx],outSCHEMAs[xx]])
        
    pool = multiprocessing.Pool(processes=12)
    pool.map(dispersal_MODEL, inPARAs)

    pool.close()
    pool.join()
    
if __name__ in ['__builtin__', '__main__']:
    
    main()
