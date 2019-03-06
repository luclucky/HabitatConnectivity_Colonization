
import numpy as np
np.set_printoptions(suppress=True)

import random

import psycopg2

import time

import re

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

import multiprocessing 
from multiprocessing import Pool

def spatialSTRESS_RAST(raster_MD, SL, numEVENTS, rAdius):
    
    grid = np.zeros((raster_MD[2], raster_MD[3]))
    
    X_DIM = np.arange(grid.shape[0])
    Y_DIM = np.arange(grid.shape[1])
    
    circles = [[random.choice(X_DIM.tolist()),random.choice(Y_DIM.tolist())] for x in range(numEVENTS)]
    
    for x in range(len(circles)):
           
        grid_INTER = np.round(np.sqrt((X_DIM[:,None] - circles[x][0]) ** 2 + (Y_DIM[None, :] - circles[x][1]) ** 2), 2)
        
        grid_INTER[grid_INTER > rAdius] = None
        
        grid_INTER = np.round(SL - (SL * (grid_INTER / rAdius)), 5)
            
        grid = np.nansum([grid_INTER, grid],axis=0)
    
    return grid

def PROBreachCONHABITAT(Co, maxCo):
    
    P = Co * 0.0
    P[np.where(Co < maxCo)] = (1 - (Co[np.where(Co < maxCo)] / maxCo))**2
    return P

def logGRO(K, N, r, t):
    
    Nt = (K * N) / (N + (K - N) * np.exp(-r*t)) 
    return Nt

def logGRO_T(T, N, r, t):

    Nt = (T * N) / (N + (T - N) * np.exp(r*t))
    return Nt

def THETAlogGRO(K, N, r, t):

    C = (K * np.sqrt(N) - N * np.sqrt(K)) / (K * N)
    Nt = K / (1 + np.exp(-theta * r * t) * C * np.sqrt(K))**2
    return Nt

def THETAlogGRO_T(T, N, r, t):
    
    C = (T * np.sqrt(N) - N * np.sqrt(T)) / (T * N)
    Nt = T / (1 + np.exp(-theta * -r * t) * C * np.sqrt(T))**2
    return Nt

def DENdepEMI_RATE(M, N, K, s):

    EmRa = N * M * (N / (K)) **(s+1)
    return EmRa

def percDISTRI_INDIdisper(COSTs, VAR):

    CO_rev = ((COSTs-max(COSTs))*-1+min(COSTs))
            
    if VAR == 'linear':
        percIND = np.round(CO_rev/sum(CO_rev),2)

    if VAR == 'exponential':   
        percIND = np.round(CO_rev**3/sum(CO_rev**3),2)
        
    return percIND            

def simSTRESS_VALUE(HQ, SL):

    STRESS = round(1-(HQ-SL)/HQ,3)
 
    return STRESS            

def randomEXT(extPROB_perRUN, occhabitats):
    
        currPROB = len(occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)) * extPROB_perRUN
       
        currPROB % 1
        
        currPROB_adj = np.random.choice([np.ceil(currPROB).astype(int), np.floor(currPROB).astype(int)], 1, p = [currPROB % 1, 1 - currPROB % 1])

        extLIST = np.random.choice(occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int), currPROB_adj)

        occhabitats[3][extLIST-1] = 0
        occhabitats[4][extLIST-1] = -111

#####

# MODEL PARAMETERS

timesteps = 100
maxCo = 1250

growthfunc = 'logGRO'    
theta = 0.5
igr = 2.0
t  = 1.0
TH = 2.0
     
m_max = 0.20
s = 0.5

extPROB_perRUN = 0.05
    
#####

def dispersal_MODEL(inPARA):
    
    conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
    cursor = conn.cursor()
        
    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """+str(inPARA[2])+""";""")
    conn.commit()
    
    cursor.execute("""SELECT tablename FROM pg_tables WHERE schemaname = '"""+str(inPARA[2])+"""';""")
    procTABs = cursor.fetchall()

    procTABs = [i[0] for i in procTABs] 

    inHABs = []

    for x in range(25):

        inHABs.append('pts_habitat_red_'+str(x+1))

    for inHAB in inHABs:
            
        for z in range(10):

            cursor.execute("""SELECT idS, st_astext(geom) FROM dis_pts_2500_10x10_"""+str(inPARA[1][-9:])+"""."""+str(inHAB)+"""_start_"""+str(z)+""";""")
            xy_pts = cursor.fetchall()
            xy_pts = [[i[0],re.findall(r"[\w']+",i[1])[1:]] for i in xy_pts]
            xy_pts = [[i[0], float(i[1][0]), float(i[1][2])] for i in xy_pts]
            xy_pts.sort()
            
            cursor.execute("""SELECT * FROM dis_pts_2500_10x10_"""+str(inPARA[1][-9:])+"""."""+str(inHAB)+"""_starthabitas;""")
            list_SH = cursor.fetchall()
            list_SH = np.array(list_SH).T

            for zz in range(10):
                
                start = time.time()
        
                cursor.execute("""SELECT start, aim, costs FROM """+str(inPARA[1])+"""."""+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+""";""")
                habitats_shortpath_red = cursor.fetchall()
                habitats_shortpath_red = [i for i in habitats_shortpath_red if i[2] <= maxCo]
                habitats_shortpath_red = np.array(habitats_shortpath_red, dtype = object).T

                habitats_qual = np.array(len(xy_pts) * [0.625])

                if str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z) in procTABs:
                    continue
                
                cursor.execute("""CREATE TABLE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+""" (pts_id BIGINT, geom GEOMETRY, hq FLOAT);""")
                
                toINS_pts = np.array(xy_pts)
                toINS_pts = toINS_pts.tolist()
                 
                for i in range(len(toINS_pts)):
                
                    toINS_pts[i][1] = 'ST_SetSRID(ST_MakePoint' + str(toINS_pts[i][1:]).replace('[','(').replace(']',')')+', 25832)'
                    toINS_pts[i][2] = str(habitats_qual[i])
                
                toINS_pts = str(np.array(toINS_pts).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
                
                cursor.execute("""INSERT INTO """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+""" (pts_id, geom, hq) values """+toINS_pts+""";""")  
                
                conn.commit()
                
                for xxxx in range(10):
                    
                    print(str(inPARA[1])+""": """+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+ ': run ' + str(xxxx))
                        
                    cursor.execute("""ALTER TABLE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+""" ADD firstcol_"""+str(xxxx+1)+"""_timestep bigint, ADD origin_"""+str(xxxx+1)+"""_timestep bigint, ADD biomass_"""+str(xxxx+1)+"""_timestep float, ADD first20_"""+str(xxxx+1)+"""_timestep bigint;""")

                    starthabitats = list_SH[xxxx]
                    
                    starthabitats_hq = habitats_qual[starthabitats-1]
                
                    occhabitats = np.array([range(len(habitats_qual)+1)[1:], [-999] * len(habitats_qual), [-999] * len(habitats_qual), [0.0] * len(habitats_qual), [-999] * len(habitats_qual)], dtype = object)
                                
                    occhabitats[1][(starthabitats-1).tolist()] = 0
                    occhabitats[2][(starthabitats-1).tolist()] = 0
                    occhabitats[3][(starthabitats-1).tolist()] = starthabitats_hq * 100.0
                    occhabitats[4][(starthabitats-1).tolist()] = 0
                
                    prob = PROBreachCONHABITAT(Co = habitats_shortpath_red[2], maxCo = maxCo)
                
                    for x in range(timesteps):
                                
                        if len(occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)) == 0:
                            break
                        
                        starthabitats = occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)

                        igr_rand = igr 
                
                        starthabitats_hq = habitats_qual[starthabitats-1] # habitat-quality of starthabitats
                        starthabitats_indnr = occhabitats[3][starthabitats-1] # number of individuals in starthabitats
                
                        if growthfunc == 'logGRO': 
                            
                            starthabitats_indnr = logGRO(K = starthabitats_hq*100, N = starthabitats_indnr, r = igr_rand, t = 1)
                
                        if growthfunc == 'logGRO_T': 
                            
                            starthabitats_indnr[np.where(starthabitats_indnr > TH)] = logGRO(K = starthabitats_hq[np.where(starthabitats_indnr > TH)]*100, N = starthabitats_indnr[np.where(starthabitats_indnr > TH)], r = igr_rand, t = 1)
                
                            starthabitats_indnr[np.where(starthabitats_indnr <= TH)] = logGRO_T(T = TH, N = starthabitats_indnr[np.where(starthabitats_indnr <= TH)], r = igr_rand, t = 1)
                            
                        if growthfunc == 'THETAlogGRO': 
                            
                            starthabitats_indnr = THETAlogGRO(K = starthabitats_hq*100, N = starthabitats_indnr, r = igr_rand, t = 1)
                
                        if growthfunc == 'THETAlogGRO_T': 
                            
                            starthabitats_indnr[np.where(starthabitats_indnr > TH)] = THETAlogGRO(K = starthabitats_hq[np.where(starthabitats_indnr > TH)]*100, N = starthabitats_indnr[np.where(starthabitats_indnr > TH)], r = igr_rand, t = 1)
                
                            starthabitats_indnr[np.where(starthabitats_indnr <= TH)] = THETAlogGRO_T(T = TH, N = starthabitats_indnr[np.where(starthabitats_indnr <= TH)], r = igr_rand, t = 1)
                            
                        occhabitats[3][starthabitats-1] = np.round(starthabitats_indnr.astype(float), 3)

                        starthabitats = starthabitats[np.where(occhabitats[3][starthabitats-1] >= 20)] # starthabitats with less than 20 individuals are remove from starthabitats 
                
                        for xx in range(len(starthabitats)):
                
                            if starthabitats[xx] in habitats_shortpath_red[0] or starthabitats[xx] in habitats_shortpath_red[1]:
                                conhabitats_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == starthabitats[xx])[0].tolist(), np.where(habitats_shortpath_red[1] == starthabitats[xx])[0].tolist()]).flat).tolist()
                                
                                conhabitats_ind = [int(i) for i in conhabitats_ind]
                                
                            else:
                                continue
                                
                            torem = []
                
                            for y in conhabitats_ind:
                                
                                if habitats_shortpath_red[0][y] != starthabitats[xx]:
                                
                                    if occhabitats[3][habitats_shortpath_red[0][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[0][y]-1]-1]*100:
                                        
                                        torem.append(y)
                                
                                else:
                                    
                                    if occhabitats[3][habitats_shortpath_red[1][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[1][y]-1]-1]*100:
              
                                        torem.append(y)
                
                            for yy in torem:
                            
                                conhabitats_ind.remove(yy)   
                
                            if conhabitats_ind == []:
                            
                                continue
                            
                            disind = DENdepEMI_RATE(M = m_max, N = occhabitats[3][starthabitats[xx]-1], K = habitats_qual[starthabitats[xx]-1]*100, s = s)
                                   
                            occhabitats[3][starthabitats[xx]-1] = occhabitats[3][starthabitats[xx]-1] - disind
                    
                            disind_part = percDISTRI_INDIdisper(COSTs = habitats_shortpath_red[2][conhabitats_ind].astype(float), VAR = 'exponential')
                
                            for xxx in conhabitats_ind:
                                                
                                disind_perc = disind * disind_part[0]
                                
                                disind_part = disind_part[1:]

                                disind_perc = disind_perc * prob[xxx]
                                     
                                if disind_perc == 0.0:
                                    
                                    continue
                                            
                                if occhabitats[0][habitats_shortpath_red[0][xxx]-1] != starthabitats[xx]:
                                    
                                    if occhabitats[1][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                                    
                                        occhabitats[1][habitats_shortpath_red[0][xxx]-1] = x+1 # ts of first population of h
                                        
                                    if occhabitats[2][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                                        
                                        occhabitats[2][habitats_shortpath_red[0][xxx]-1] = starthabitats[xx] # h populated from which sh
                                                
                                    if occhabitats[3][habitats_shortpath_red[0][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[0][xxx]-1]-1]*100): # max pop size hq * 100        
                                                                                   
                                        occhabitats[3][habitats_shortpath_red[0][xxx]-1] = occhabitats[3][habitats_shortpath_red[0][xxx]-1] + disind_perc # function to calculate number of individuals in h -> plus disind_perc
                                        
                                    if  occhabitats[4][habitats_shortpath_red[0][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[0][xxx]-1] >= 20.0:
                                        occhabitats[4][habitats_shortpath_red[0][xxx]-1] = x+1
                                        
                                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[0][xxx]-1]]), return_index=True)
                                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                                    
                                if occhabitats[0][habitats_shortpath_red[1][xxx]-1] != starthabitats[xx]:
                                       
                                    if occhabitats[1][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                                                                
                                        occhabitats[1][habitats_shortpath_red[1][xxx]-1] = x+1 # ts of first population of h
                                    
                                    if occhabitats[2][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                
                                        occhabitats[2][habitats_shortpath_red[1][xxx]-1] = starthabitats[xx] # h populated from which sh
                                    
                                    if occhabitats[3][habitats_shortpath_red[1][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[1][xxx]-1]-1]*100): # max pop size hq * 100                
                
                                        occhabitats[3][habitats_shortpath_red[1][xxx]-1] = occhabitats[3][habitats_shortpath_red[1][xxx]-1] + disind_perc# function to calculate number of individuals in h -> plus disind_perc
                                  
                                    if  occhabitats[4][habitats_shortpath_red[1][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[1][xxx]-1] >= 25:
                                        occhabitats[4][habitats_shortpath_red[1][xxx]-1] = x+1
                                        
                                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[1][xxx]-1]]), return_index=True)
                                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                
                    occhabitats[3] = occhabitats[3] * 25.0 # conversion into mg biomass   
                          
                    toins = str(np.array(occhabitats).T.tolist())[1:-1].replace('[','(').replace(']',')')
                    
                #####
                    
                    cursor.execute("""UPDATE """+str(inPARA[2])+"""."""+str(inPARA[0])+"""_50x50_"""+str(zz)+"""_"""+str(inHAB[16:])+"""_start_"""+str(z)+""" SET firstcol_"""+str(xxxx+1)+"""_timestep = firstcol_"""+str(xxxx+1)+"""_timestep_arr, origin_"""+str(xxxx+1)+"""_timestep = origin_"""+str(xxxx+1)+"""_timestep_arr, biomass_"""+str(xxxx+1)+"""_timestep = biomass_"""+str(xxxx+1)+"""_timestep_arr, first20_"""+str(xxxx+1)+"""_timestep = first20_"""+str(xxxx+1)+"""_timestep_arr from (values """+toins+""") as c(pts_id_arr, firstcol_"""+str(xxxx+1)+"""_timestep_arr, origin_"""+str(xxxx+1)+"""_timestep_arr, biomass_"""+str(xxxx+1)+"""_timestep_arr, first20_"""+str(xxxx+1)+"""_timestep_arr) WHERE pts_id = pts_id_arr;""") 
                
                conn.commit()
                
                end = time.time()
                print((end - start) / 60)

    cursor.close()
    conn.close()

#####

def main():

    inSCHEMAs = ['stream_network_000050050_linear_02', 'stream_network_025375375_linear_02', 'stream_network_075125125_linear_02', 'stream_network_100000000_linear_02', 'stream_network_050000050_linear_02','stream_network_375025375_linear_02', 'stream_network_125075125_linear_02', 'stream_network_000100000_linear_02', 'stream_network_050050000_linear_02', 'stream_network_375375025_linear_02','stream_network_125125075_linear_02', 'stream_network_000000100_linear_02', 'stream_network_050025025_linear_02', 'stream_network_025050025_linear_02', 'stream_network_025025050_linear_02']
    
    outSCHEMAs = ['stream_network_000050050_linear_02_results', 'stream_network_025375375_linear_02_results', 'stream_network_075125125_linear_02_results', 'stream_network_100000000_linear_02_results', 'stream_network_050000050_linear_02_results','stream_network_375025375_linear_02_results', 'stream_network_125075125_linear_02_results', 'stream_network_000100000_linear_02_results', 'stream_network_050050000_linear_02_results', 'stream_network_375375025_linear_02_results','stream_network_125125075_linear_02_results', 'stream_network_000000100_linear_02_results', 'stream_network_050025025_linear_02_results', 'stream_network_025050025_linear_02_results', 'stream_network_025025050_linear_02_results']
     
    inNLMs = ['habitats_shortpath_red_nlmr_testarea', 'habitats_shortpath_red_nlmrc_testarea', 'habitats_shortpath_red_nlmre_testarea']
    
    inPARAs = []
    
    for a in range(len(inNLMs)):
        
        for aa in range(len(inSCHEMAs)):
        
            inPARAs.append([inNLMs[a],inSCHEMAs[aa],outSCHEMAs[aa]])
        
    pool = multiprocessing.Pool(processes=12)
    pool.map(dispersal_MODEL, inPARAs)

    pool.close()
    pool.join()
    
if __name__ in ['__builtin__', '__main__']:
    
    main()
