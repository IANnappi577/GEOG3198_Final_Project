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
    # load the raw CSV
    temp_csv = pd.read_csv(f'../data/temperature_data/{year}_temperature_raw.csv')

    # convert to a GeoDataFrame using the existing lat/long coords
    temp = gpd.GeoDataFrame(temp_csv, geometry=gpd.points_from_xy(temp_csv.LONGITUDE, temp_csv.LATITUDE), crs='EPSG:4326')

    # drop unnecessary columns, which differ whether this is the 2015 or 2025 data:
    if(year == '2015'):
        temp.drop(columns=['LATITUDE', 'LONGITUDE', 'AWND', 'WSFG', 'DX70', 'TMAX', 'TAVG', 'EMXT'], inplace=True)
    else:
        temp.drop(columns=['LATITUDE', 'LONGITUDE', 'DX70', 'TMAX', 'TAVG', 'EMXT'], inplace=True)

    # Remove the weather stations that do not have the variable that we need: Number of Max Heat days, or DX90
    # i.e., we will remove the weather stations for which DX90 is null
    temp = temp[temp["DX90"].notna()]

    # reproject to the final projection
    temp.to_crs(PROJECTION, inplace=True)

    # Load the census tracts
    census_bounds = gpd.read_file(f'../data/tigerline_shapefiles/tigerline_{year}_tract/tl_{year}_11_tract.shp')
    # Reproject the census tracts
    census_bounds.to_crs(PROJECTION, inplace=True)

    # Now for each polygon in the census tract shapefile, we want to find the closest point (weather station) 
    # and assign the DX90 value from that point to that census tract.
    # We will use a form of sjoin called sjoin_nearest, which will find the closest polygon per point.
    
    # Here is a tutorial I followed to understand the syntax for a similar task:
    # https://stackoverflow.com/questions/72639523/question-on-geopandas-spatial-join-nearest
    joined_points_polygons = gpd.sjoin_nearest(
        census_bounds, # polygon geometry
        temp, # point geometry
        how = 'left',
        # we will leave out 'max_distance' from the tutorial
        distance_col = "distances"  # I suppose this is a column for the min distance it found between polygon/point
    )

    # Visualize the output
    m = joined_points_polygons.explore()
    m = temp.explore(m=m, color='Red')
    m.save(f'joined_points_polygons_{year}.html')
    webbrowser.open('file://' + os.path.realpath(f'joined_points_polygons_{year}.html'))

    # Export to GeoJSON
    joined_points_polygons.to_file(f'../data/temperature_data/{year}_extemp_census_tract.geojson')


#####################################
# Run the above function for both years
clean_extreme_heat_days('2015')
clean_extreme_heat_days('2025')