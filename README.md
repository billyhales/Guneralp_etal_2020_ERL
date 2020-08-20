# Trends in urban land expansion, density, and land transitions from 1970 to 2010: a global synthesis </h1>
### Burak Güneralp, Meredith Reba, Billy U Hales, Elizabeth A Wentz, Karen C Seto. <br/> </h3>
#### Environmental Research Letters. 15(4) 044015. <br/> </h4>
https://doi.org/10.1088/1748-9326/ab6669

This repository contains code that is used to analyze data and generate figures within the above research work.

## Items in Repository
+ Code
    * **Figure_1_3_S3_Locations_WUP300K.py**
    
      This script creates all the plots to make Figures 1, 3, and S3 in **Güneralp *et.al.* (2020)** with input file, Input_ranked-by-LocationName_WUP300K.csv.
      
      **Example commandline:**
      `python ./Figure_1_3_S3_Locations_WUP300K.py Input_ranked-by-LocationName_WUP300K.csv`
      
+ Data
    * **Input_ranked-by-LocationName_WUP300K.csv**
    
      This file represnts the processed data that is input into the script, Figure_1_3_S3_Locations_WUP300K.py, to make the plots necessary to make Figures 1,3,S3.

+ Documentation
    * **Key-for-Input_ranked-by-LocationName_WUP300K.txt**
      This is the file that identifies the purpose of different column names within the input file under **Data**
      
+ Output
    * ***.png**
    
      These are the output plots that the script, **Figure_1_3_S3_Locations_WUP300K.py** generates from **Input_ranked-by-LocationName_WUP300K.csv**.
      
    * **regional_location_bstrap.xlsx**
    
      This file contains the bootstrapped estimates (n=1000) per size class (n=3), decade(n=5) or decade-intervals(n=4), and region (n=10).
      
    * **regional_location_summary.csv**
    
      This file contains the means and medians of bootstrapped estimates for all the types discussed in the description of regional_location_bstrap.xlsx
      
Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
