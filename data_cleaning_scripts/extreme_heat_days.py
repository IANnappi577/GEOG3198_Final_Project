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

# ----- 2015 data cleaning ----- #

# load raw CSV
temp_2015_csv = pd.read_csv('../data/temperature_data/2015_temperature_raw.csv')

# convert to GeoDataFrame
temp_2015 = gpd.GeoDataFrame(temp_2015_csv, geometry=gpd.points_from_xy(temp_2015_csv.LONGITUDE, temp_2015_csv.LATITUDE), crs='EPSG:4326')

# drop unnecessary columns
# the columns AWND and WSFG (related to wind variables) were dropped because most stations did not have data for them
temp_2015.drop(columns=['LATITUDE', 'LONGITUDE', 'AWND', 'WSFG'], inplace=True)

# reproject to the final ürojection
temp_2015.to_crs(PROJECTION, inplace=True)

# visualize the output
print('---- 2015 data ----')
print(temp_2015.head(5))
print('Columns:', temp_2015.columns)
print('-------------------\n')
# uncomment the following if you want to view the station locations on the map
# m = temp_2015.explore()
# m.save('temp_2015.html')
# webbrowser.open('file://' + os.path.realpath('temp_2015.html'))

# Export to GeoJSON
temp_2015.to_file('../data/temperature_data/2015_temperature_final.geojson')

# ----- 2025 data cleaning ----- #

# load raw CSV
temp_2025_csv = pd.read_csv('../data/temperature_data/2025_temperature_raw.csv')

# convert to GeoDataFrame
temp_2025 = gpd.GeoDataFrame(temp_2025_csv, geometry=gpd.points_from_xy(temp_2025_csv.LONGITUDE, temp_2025_csv.LATITUDE), crs='EPSG:4326')

# drop unnecessary columns
temp_2025.drop(columns=['LATITUDE', 'LONGITUDE'], inplace=True)

# reproject to the final projection
temp_2025.to_crs(PROJECTION, inplace=True)

# visualize the output
print('---- 2025 data ----')
print(temp_2025.head(5))
print('Columns:', temp_2025.columns)
print('-------------------')
# uncomment the following if you want to view the station locations on the map
# m = temp_2025.explore()
# m.save('temp_2025.html')
# webbrowser.open('file://' + os.path.realpath('temp_2025.html'))

# Export to GeoJSON
temp_2025.to_file('../data/temperature_data/2025_temperature_final.geojson')