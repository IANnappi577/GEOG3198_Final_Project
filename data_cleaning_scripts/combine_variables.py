import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------- Purpose -------------------- # 
# Combines all of the variables from all of the data cleaning scripts: clip_prisms.py, average_zonal_stats.py, 
#       extreme_heat_days.py, green_spaces.py, and demographics.py into one final .geojson of all of the variables
#       in appropriately-labeled columns of a GeoDataFrame per census tract.

# Final variables:
# - DX90               --> number of extreme heat days > 90 deg
# - distances          --> the distance from each census tract to the weather station that produced DX90. Not
#                          too important, but may be useful. 
# - mean_imperv_{year} --> NOTE: the year is 2024 for the later one, not 2025
# - Perc_un_5          --> Percent of the population under 5 yrs old, in decimal percent from 0-1, multiply by 100 to get 0-100%
# - Perc_ov_65         --> Percent of the population over 65 yrs old, in decimal percent from 0-1
# - Perc_disabl        --> Percent of the population that is disabled, in decimal percent from 0-1
# - Perc_in_pov        --> Percent of the population under the poverty line, in decimal percent from 0-1
# - mean_tdmean_{year} --> The average dew point over the months May - September
# - mean_tmax_{year}   --> The average maximum temperature over the months May - September
# ...Where each {year} here is either 2015 or 2025

# Notes:
# Weigh the # of extreme heat days LESS than the prism data, because there are only 3-4 different values and they
# are NOT very different, it's like all like 1-2 values for the entirety of DC...
# If you really want, you can add the variety of the distance to the stations to add variation, but that may be too much...

def combine_variables(year: str):
    
    # Load all the variables as seperate GEOJSONs
    
    ##########################
    # Number of Extreme Temperature Days
    ex_temp = gpd.read_file(f'../data/temperature_data/{year}_extemp_census_tract.geojson')

    ##########################
    # Percent Impervious Surface
    if(year == '2025'):
        census_year = '2024'
    else:
        census_year = '2015'
    green_areas = gpd.read_file(f'../data/green_areas/NLCD_{census_year}/census_imperv_surface_{census_year}.geojson')

    ##########################
    # Demographics Data
    demographics = gpd.read_file(f'../data/demographic_data/final_tables/{year}_final_stats.geojson')

    ##########################
    # PRISM data / tdmean - mean dew point
    tdmean = gpd.read_file(f'../data/tdmean/{year}/summary_statistics_{year}.geojson')

    ##########################
    # PRISM data / tmax - maximum average temperature
    tmax = gpd.read_file(f'../data/tmax/{year}/summary_statistics_{year}.geojson')

    # Join everything to the ex_temp dataframe
    # Drop all columns other than the GEOID, which will be used to join on every other dataframe
    green_areas = green_areas[['GEOID', f'mean_imperv_{census_year}']].copy()
    demographics = demographics[['GEOID', 'Perc_un_5', 'Perc_ov_65', 'Perc_disabl', 'Perc_in_pov']].copy()
    tdmean = tdmean[['GEOID', f'mean_tdmean_{year}']].copy()
    tmax = tmax[['GEOID', f'mean_tmax_{year}']].copy()

    # Merge all dataframes to the ex_temp dataframe using the GEOID
    final_statistics = pd.merge(ex_temp, green_areas, how='inner', left_on='GEOID', right_on='GEOID')
    final_statistics = pd.merge(final_statistics, demographics, how='inner', left_on='GEOID', right_on='GEOID')
    final_statistics = pd.merge(final_statistics, tdmean, how='inner', left_on='GEOID', right_on='GEOID')
    final_statistics = pd.merge(final_statistics, tmax, how='inner', left_on='GEOID', right_on='GEOID')

    # Drop last unnecessary columns
    final_statistics = final_statistics[['GEOID', 'DX90', 'distances', f'mean_imperv_{census_year}', 'Perc_un_5',
            'Perc_ov_65', 'Perc_disabl', 'Perc_in_pov', f'mean_tdmean_{year}', f'mean_tmax_{year}', 'geometry']].copy()

    # Export to final geojson
    final_statistics.to_file(f'../data/final_cleaned_data/{year}_final_cleaned_dataframe.geojson')
    print(f'Success! Exported the final {year} statistics file')


#####################################
# Run the above function for both years
combine_variables('2015')
combine_variables('2025')