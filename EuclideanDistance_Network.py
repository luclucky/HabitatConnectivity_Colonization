
import numpy as np
        
import psycopg2

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

cursor.execute("""SELECT ids FROM stream_network.pts_habitat""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]


ids_toDEL = []

for x in ids:
    
    print(x)
    
    if x not in ids_toDEL:
        
        cursor.execute("""SELECT ids FROM stream_network.pts_habitat WHERE ST_DWithin(geom, (SELECT geom FROM stream_network.pts_habitat WHERE ids = """+str(x)+"""), 99)  AND ids !=  """+str(x)+""";""")
        
        toEXT = [i[0] for i in cursor.fetchall()]
        
        ids_toDEL.extend(toEXT)
        
    cursor.execute("""CREATE TABLE stream_network.pts_habitat_red AS SELECT geom FROM stream_network.pts_habitat WHERE ids NOT IN ("""+str(ids_toDEL)[1:-1].replace("L", "")+""");""")

    cursor.execute("""ALTER TABLE stream_network.pts_habitat_red ADD column IDs bigserial;""")
    
    conn.commit()


cursor.execute("""CREATE TABLE stream_network.dist_pts_2500 AS SELECT * FROM public.dist_pts_2500;""")

cursor.execute("""DELETE FROM stream_network.dist_pts_2500;""")

conn.commit()

cursor.execute("""SELECT ids FROM stream_network.pts_habitat_red""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:
    
    print(x)
    
    cursor.execute("""INSERT INTO stream_network.dist_pts_2500 SELECT a.ids AS start, ST_AsText(a.geom) AS start_xy, b.ids AS aim, ST_AsText(b.geom) AS aim_xy, ST_makeline(a.geom, b.geom) AS geom, ST_Distance(a.geom, b.geom) AS distance FROM (SELECT * FROM stream_network.pts_habitat_red WHERE ids = """+str(x)+""")  a, (SELECT * FROM stream_network.pts_habitat_red WHERE ST_DWithin(geom, (SELECT geom FROM stream_network.pts_habitat_red WHERE ids = """+str(x)+"""), 2500))  b WHERE a.ids <> b.ids;""")
    
    conn.commit()

