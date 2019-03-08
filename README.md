
### FRAMEWORK, INPUT-DATA & PYTHON CODE 

# HOW DOES HABITAT CONNECTIVITY INFLUENCE THE COLONIZATION SUCCESS OF AN AQUATIC HEMIMETABOLOUS INSECT?

Lucas Streib¹, Henriette Heer¹, Mira Kattwinkel¹, Stefan Ruzika², Ralf B. Schäfer¹

¹Institute for Environmental Sciences, University Koblenz-Landau, 76829 Landau i. d. Pfalz, Germany\
² Department of Mathematics, University of Kaiserslautern, 67653 Kaiserslautern, Germany

## A. FRAMEWORK

### Hardware

System memory: 31.4 GiB\
Processor: Intel® Xeon(R) CPU E5-2680 v3 @ 2.50GHz x 16

### OPERATING SYSTEM

Ubuntu Version 18.04.1 LTS (Bionic Beaver) 64-bit\
Kernel Linux 4.15.0-45-generic x86_64\
MATE 1.20.1

### SOFTWARE

PostgreSQL 9.6.10\
PostGIS 2.3.3\
Python 2.7.12

### PYTHON LIBRARIES

gdal 2.2.1\
multiprocessing 0.70a1\
nlmpy 0.1.5\
numpy 1.11.0\
os\
psycopg2 2.7.6.1\
random\
re 2.2.1\
scikit-image 0.10.1 see http://scikit-image.org/docs/dev/api/skimage.graph.html \
subprocess

## B. INPUT-DATA

## C. PYTHON CODE

**psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")** see http://initd.org/psycopg/docs/module.html

Please run the scripts in the following order:

#### 1. Landscape_Scenarios.py


#### 2. EuclideanDistance_Networks.py


#### 3. Patch_Arragments.py


#### 4. Habitat_Networks.py


#### 5. Simulation.py



