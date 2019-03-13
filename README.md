
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

All results produced by the **PYTHON CODE** (see C.) will be stored in a PostgreSQL database extended by PostGIS. The simulation 

Following **PYTHON LIBRARIES** are required: 

- gdal 2.2.1
- multiprocessing 0.70a1
- nlmpy 0.1.5
- numpy 1.11.0
- os
- psycopg2 2.7.6.1
- random
- re 2.2.1
- scikit-image 0.10.1 see http://scikit-image.org/docs/dev/api/skimage.graph.html 
- subprocess

### B. INPUT-DATA

geoDATA_gitHUB

tiles_10x10km.shp
habitat_patches.shp

### C. PYTHON CODE

**psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")** see http://initd.org/psycopg/docs/module.html

*** 1. Landscape_Scenarios.py ***

*** 2. EuclideanDistance_Networks.py ***

*** 3. Patch_Arragments.py ***

*** 4. Habitat_Networks.py ***

*** 5. Simulation.py ***


Please run the scripts corresponding their numerical order.

For suggestions or requests for further information please contact the corresponding author Lucas Streib:\

Phone:  +49 6341 280-32317
Mail:   streib@uni-landau.de

Institute for Enviornmental Sciences\ 
Quantitative Landscape Ecology\
University of Koblenz-Landau, Campus Landau\
Fortstraße 7\
76829 Landau / Pfalz\
Germany

