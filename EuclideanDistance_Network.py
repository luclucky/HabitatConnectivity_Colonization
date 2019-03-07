
import numpy as np
        
import psycopg2

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

cursor.execute("""SELECT ids FROM stream_network.pts_habitat_red""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:
    
    print(x)
    
    cursor.execute("""INSERT INTO stream_network.dist_pts_2500 SELECT a.ids AS start, ST_AsText(a.geom) AS start_xy, b.ids AS aim, ST_AsText(b.geom) AS aim_xy, ST_makeline(a.geom, b.geom) AS geom, ST_Distance(a.geom, b.geom) AS distance FROM (SELECT * FROM stream_network.pts_habitat_red WHERE ids = """+str(x)+""")  a, (SELECT * FROM stream_network.pts_habitat_red WHERE ST_DWithin(geom, (SELECT geom FROM stream_network.pts_habitat_red WHERE ids = """+str(x)+"""), 2500))  b WHERE a.ids <> b.ids;""")
    
    conn.commit()

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:

    cursor.execute("""CREATE TABLE stream_network_10x10.dist_pts_2500_50x50_""" + str(x) + """ AS SELECT * FROM stream_network.dist_pts_2500_50x50 WHERE ST_Contains((SELECT geom FROM stream_network.rast_10x10 WHERE ids = """ + str(x) + """), geom);""")

    conn.commit()

cursor.close()
conn.close()
