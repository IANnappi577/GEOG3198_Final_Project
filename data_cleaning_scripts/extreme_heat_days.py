import geopandas as gpd
import pandas as pd
import webbrowser
import os
from config import PROJECTION

# -------------
# Purpose: clean the data related to physical temperature variables and export to an appropriate format
# -- File Dependencies:
#    -- /data/temperature_data/
#         - 2015_temperature_raw.csv
#         - 2025_temperature_raw.csv
# -------------

# Make this a function to repurpose for both 2015 and 2025
def clean_extreme_heat_days(year: str):
    # load raw CSV
    temp_csv = pd.read_csv(f'../data/temperature_data/{year}_temperature_raw.csv')

    # convert to GeoDataFrame
    temp = gpd.GeoDataFrame(temp_csv, geometry=gpd.points_from_xy(temp_csv.LONGITUDE, temp_csv.LATITUDE), crs='EPSG:4326')

    # drop unnecessary columns
    # the columns AWND and WSFG (related to wind variables) were dropped because most stations did not have data for them
    if(year == '2015'):
        temp.drop(columns=['LATITUDE', 'LONGITUDE', 'AWND', 'WSFG', 'DX70', 'TMAX', 'TAVG', 'EMXT'], inplace=True)
    else:
        temp.drop(columns=['LATITUDE', 'LONGITUDE', 'DX70', 'TMAX', 'TAVG', 'EMXT'], inplace=True)

    # Remove the weather stations that do not have the variable that we need: Number of Max Heat days, or DX90
    # i.e., the weather stations for which DX90 is null
    temp = temp[temp["DX90"].notna()]

    # reproject to the final projection
    temp.to_crs(PROJECTION, inplace=True)

    # Load the census tracts
    census_bounds = gpd.read_file(f'../data/tigerline_shapefiles/tigerline_{year}_tract/tl_{year}_11_tract.shp')
    # Reproject the census tracts
    census_bounds.to_crs(PROJECTION, inplace=True)

    # Now for each polygon in the census tract shapefile, we want to find the closest point (weather station) 
    # value and assign the DX90 value from that point to that census tract.
    
    # Follow this tutorial for sjoin_nearest points to polygons
    # https://stackoverflow.com/questions/72639523/question-on-geopandas-spatial-join-nearest
    # result = tracts_gdf.sjoin_nearest(
    #     points_gdf,
    #     how="left",
    #     distance_col="distance"
    # )

    # TODO: temp assign the mean value of the column to the census tracts
    census_bounds['Ex_Heat_Days'] = temp['DX90'].mean()
    print(census_bounds.head(5))

    # Export to GeoJSON
    census_bounds.to_file(f'../data/temperature_data/{year}_extemp_census_tract.geojson')


#####################################
# Run the above function for both years
clean_extreme_heat_days('2015')
clean_extreme_heat_days('2025')