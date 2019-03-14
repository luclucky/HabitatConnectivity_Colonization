
## FRAMEWORK, INPUT-DATA & PYTHON CODE FOR THE PUBLICATION:

# HOW DOES HABITAT CONNECTIVITY INFLUENCE THE COLONIZATION SUCCESS OF AN AQUATIC HEMIMETABOLOUS INSECT? - A MODELLING APPROACH

Lucas Streib¹, Henriette Heer¹, Mira Kattwinkel¹, Stefan Ruzika², Ralf B. Schäfer¹

¹ Institute for Environmental Sciences, University Koblenz-Landau, 76829 Landau i. d. Pfalz, Germany\
² Department of Mathematics, University of Kaiserslautern, 67653 Kaiserslautern, Germany

### A. FRAMEWORK

The **SOFTWARE-FRAMEWORK** for the presented meta-population model consists of: 

- [PostgreSQL 9.6.10](https://www.postgresql.org/docs/9.6/release-9-6-10.html)
- [PostGIS 2.3.3](https://postgis.net/2017/07/01/postgis-2.3.3/)
- [Python 2.7.12](https://www.python.org/downloads/release/python-2712/)

All results produced by the **PYTHON CODE** (see C.) will be stored in a [PostgreSQL](https://www.postgresql.org/) database extended by [PostGIS](https://postgis.net/). The set-up of landscape scenarios, habitat networks and the simulation is implemented in **PYTHON** using the PostgreSQL database adapter [Psycopg](http://initd.org/psycopg/docs/index.html).\
To run the code following **PYTHON LIBRARIES** are further required: 

- [gdal 2.2.1](https://pypi.org/project/pygdal/)
- [multiprocessing 0.70a1](https://pypi.org/project/multiprocess/)
- [nlmpy 0.1.5](https://pypi.org/project/nlmpy/)
- [numpy 1.11.0](https://pypi.org/project/numpy/)
- os
- [psycopg2 2.7.6.1](https://pypi.org/project/psycopg2/)
- random
- re 2.2.1
- [scikit-image 0.10.1](http://scikit-image.org/docs/dev/api/skimage.graph.html) 
- subprocess

### B. INPUT-DATA

Following three geo-datasets are required as **INPUT-DATA**:

 - **stream_net.tif**:\
   Raster dataset (resolution 25m x 25m) representing a 50 * 50 km section of a stream network from South-West Germany 
 - **habitat_patches.shp**:\
   Point-Shapefile dataset representing centroids of potential habitat patches along the stream network with an interval of 100 meters.
 - **tiles_10x10km.shp**:\
   Polygon-Shapefile dataset representing 25 coextensive squares covering the raster dataset. 

The datasets are stored in the repository folder [geoDATA](https://github.com/luclucky/HabitatConnectivity_Colonization/tree/master/geoDATA_gitHUB) and have initially be imported into the database-schema **stream_network**; accordingly the schema has to be created and named in advance. For the import into the database see e.g. [PostGIS 2.4.8dev Manual](https://postgis.net/stuff/postgis-2.4.pdf) - 4.4.Loading GIS (Vector) Data & 5.1 Loading and Creating Rasters. 

### C. PYTHON CODE

For database access from Python first, the connection parameters have to be specified in of the scripts stored in the repository folder [pythonCODE](https://github.com/luclucky/HabitatConnectivity_Colonization/tree/master/pythonCODE). Therefore, replace **???**-symbols in the command **psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")** found in each script according to the [psycopg manual](http://initd.org/psycopg/docs/module.html).
The individual code is commented regarding specific implementation details, variable declarations, data storage etc..\ 
Please run the scripts corresponding following order:

**1. Landscape_Scenarios.py**\
**2. EuclideanDistance_Networks.py**\
**3. Patch_Arragments.py**\
**4. Habitat_Networks.py**\
**5. Simulation.py**\

------

For suggestions or requests for further information please contact the corresponding author **Lucas Streib**:\

&#9993; streib@uni-landau.de\
&#9990; +49 6341 280-32317\

Institute for Enviornmental Sciences\
Quantitative Landscape Ecology\
University of Koblenz-Landau, Campus Landau\
Fortstraße 7\
76829 Landau\
Germany

