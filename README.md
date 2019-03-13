
## FRAMEWORK, INPUT-DATA & PYTHON CODE 

# HOW DOES HABITAT CONNECTIVITY INFLUENCE THE COLONIZATION SUCCESS OF AN AQUATIC HEMIMETABOLOUS INSECT? - A MODELLING APPROACH

Lucas Streib¹, Henriette Heer¹, Mira Kattwinkel¹, Stefan Ruzika², Ralf B. Schäfer¹

¹ Institute for Environmental Sciences, University Koblenz-Landau, 76829 Landau i. d. Pfalz, Germany\
² Department of Mathematics, University of Kaiserslautern, 67653 Kaiserslautern, Germany

### A. FRAMEWORK

The **SOFTWARE-FRAMEWORK** for the presented meta-population model consists of: 

- PostgreSQL 9.6.10
- PostGIS 2.3.3
- Python 2.7.12

All results produced by the **PYTHON CODE** (see C.) will be stored in a PostgreSQL database extended by PostGIS. The set-up of landscape scenarios, habitat networks and the simulation is implemented in **PYTHON** using the PostgreSQL database adapter **Psycopg**.\
To run the **PYTHON CODE**, beside **PostGIS** following **PYTHON LIBRARIES** are required: 

- gdal 2.2.1
- multiprocessing 0.70a1
- nlmpy 0.1.5
- numpy 1.11.0
- os
- psycopg2 2.7.6.1
- random
- re 2.2.1
- scikit-image 0.10.1 (see http://scikit-image.org/docs/dev/api/skimage.graph.html) 
- subprocess

### B. INPUT-DATA

The three geo-datasets stored in the repository folder [geoDATA_gitHUB](https://github.com/luclucky/HabitatConnectivity_Colonization/tree/master/geoDATA_gitHUB):

- stream_net.tif
- tiles_10x10km.shp
- habitat_patches.shp

**geoDATA_gitHUB** 

Therefore a schema named **stream_network** has to be created in the database and the geo-datasets have to be imported. For the import see **PostGIS 2.4.8dev Manual** - 4.4.Loading GIS (Vector) Data & 5.1 Loading and Creating Rasters (https://postgis.net/stuff/postgis-2.4.pdf)


stream_net.tif
tiles_10x10km.shp
habitat_patches.shp

### C. PYTHON CODE

**???**

**psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")** see http://initd.org/psycopg/docs/module.html

**1. Landscape_Scenarios.py**

**2. EuclideanDistance_Networks.py**

**3. Patch_Arragments.py**

**4. Habitat_Networks.py**

**5. Simulation.py**

Please run the scripts corresponding their numerical order.

------

For suggestions or requests for further information contact the corresponding author Lucas Streib:\

Phone:  +49 6341 280-32317\
Mail:   streib@uni-landau.de\

Institute for Enviornmental Sciences\ 
Quantitative Landscape Ecology\
University of Koblenz-Landau, Campus Landau\
Fortstraße 7\
76829 Landau / Pfalz\
Germany

