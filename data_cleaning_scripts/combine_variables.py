import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import sys

# -------------------- Purpose -------------------- # 
# Combines all of the variables from all of the data cleaning scripts: clip_prisms.py, average_zonal_stats.py, 
#       extreme_heat_days.py, green_spaces.py, and demographics.py into one final .geojson of all of the variables
#       in appropriately-labeled columns of a GeoDataFrame per census tract.

# Final variables:
# - ex_temp         --> number of extreme heat days > 90 deg
# - per_imperv_surf --> 

def combine_variables(year: str):
    
    # Load all the variables as seperate GEOJSONs
    
    ##########################
    # Number of Extreme Temperature Days
    ex_temp = gpd.read_file(f'../data/temperature_data/{year}_extemp_census_tract.geojson')
    print(ex_temp.crs)

    ##########################
    # Percent Impervious Surface
    if(year == '2025'):
        census_year = '2024'
    else:
        census_year = '2015'
    green_areas = gpd.read_file(f'../data/green_areas/NLCD_{census_year}/census_imperv_surface_{census_year}.geojson')
    print(green_areas.head(5))
    print(green_areas.crs)

    ##########################
    # Demographics Data
    # demographics = gpd.read_file(f'../data/demographic_data/final_tables/')

    green_areas.to_file(f'../data/final_cleaned_data/{year}_final_cleaned_dataframe.geojson')

    print(1)

combine_variables('2015')
combine_variables('2025')