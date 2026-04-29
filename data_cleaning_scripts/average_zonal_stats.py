import geopandas as gpd
import pandas as pd
import rasterio
from rasterstats import zonal_stats
import numpy as np
import matplotlib.pyplot as plt
from config import PROJECTION
import sys

# -------------------- Purpose -------------------- # 
# Pull the stacked bands, perform an average of tmax across all bands to get the average over all months,
# then do zonal statistics to summarize per tigerline census tract

# ------------------ Requirements ----------------- #
# Takes in exactly 1 command line arguments: the variable you are computing zonal stats for. Possible 
# choices: ['tdmean', 'tmax']

# Load command line arguments
if(len(sys.argv) != 2):
    print('''Incorrect number of command line arguments!
Exactly 1 argument is required: the variable you are computing zonal stats on. The possible choices are: tdmean OR tmax.
Please run either:
    python3 average_zonal_stats.py tdmean  OR
    python3 average_zonal_stats.py tmax''')
    sys.exit(0)
    
# Note to self: sys.argv[0] -> program called, ignore this
variable = str(sys.argv[1])

# Load census tract boundaries
census_bounds = gpd.read_file('../data/tigerline_shapefiles/tigerline_2015_tract/tl_2015_11_tract.shp')
# temporarily reproject to the CRS of the rasters
census_bounds.to_crs('EPSG:4269', inplace=True)

# Create a copy of the census tract boundaries that will serve as the main dataframe 
# for final summarized statistics
summarized_stats = census_bounds.copy()
summarized_stats.drop(columns=['NAMELSAD', 'MTFCC', 'FUNCSTAT', 'STATEFP', 'COUNTYFP', 'INTPTLAT', 'INTPTLON'], inplace=True)

#####################################
# Since the steps for 2015 and 2025 are similar, define a function that will be run twice for both years
def average_zonal_stats_by_year(year: str):
    # Compute the average across all month bands to get the average per month

    # Load the stacked, clipped raster
    with rasterio.open(f'../data/{variable}/{year}/{variable}_months_stacked_clipped_{year}.tif') as src:
        # read all of the bands
        all_months = src.read()

        # replace the nodata value (-9999) to np.nan
        all_months.astype(np.float32)
        all_months[all_months == -9999] = np.nan

        # Compute the average across all of the bands to collapse down to a single-band raster
        avg_across_months = np.nanmean(all_months, axis=0)

        # write the result to an output file
        avg_profile = src.profile.copy()
        avg_profile.update({
            'count': 1,  # now we only habe 1 band
            'nodata': np.nan,  # since avg is a float we need to store this as a float now
            'dtype': 'float32' # data type is now float
        })

        with rasterio.open(f'../data/{variable}/{year}/{variable}_averaged.tif', 'w', **avg_profile) as dst:
            dst.write(avg_across_months, 1)

    # Compute the mean for each census tract using zonal_stats()
    # Since the pixels are so large, all_touched here will make a difference in the result. We'll
    # choose all_touched=True because the large pixels near the edge should NOT be excluded to calculate a more
    # accurate mean
    mean_per_census_tract = zonal_stats(
        vectors=census_bounds,
        raster=f'../data/{variable}/{year}/{variable}_averaged.tif',
        nodata=np.nan,
        stats=['mean'],
        all_touched=True
    )
    # Convert to a pandas DataFrame
    mean_per_census_tract = pd.DataFrame(mean_per_census_tract)

    # Add the mean to the summary dataframe (summarized_stats)
    summarized_stats[f'mean_{variable}_{year}'] = mean_per_census_tract['mean']


#####################################
# Run the above function for both years
average_zonal_stats_by_year('2015')
average_zonal_stats_by_year('2025')


#####################################
# save the summary statistics to the summary statistics geodataframe
# Reproject to the final projection
summarized_stats.to_crs(PROJECTION, inplace=True)
# save the file to geojson
summarized_stats.to_file(f'../data/{variable}/summary_statistics.geojson')


#####################################
# visualize the final results
with rasterio.open(f'../data/{variable}/2015/{variable}_averaged.tif') as src:
    prism_data_2015 = src.read(1)

with rasterio.open(f'../data/{variable}/2025/{variable}_averaged.tif') as src:
    prism_data_2025 = src.read(1)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(20, 5))

# raster visualizations
im1 = ax1.imshow(prism_data_2015, cmap='Greens')
ax1.set_title(f'2015 {variable}')
plt.colorbar(im1, ax=ax1)

im2 = ax2.imshow(prism_data_2025, cmap='Greens')
ax2.set_title(f'2025 {variable}')
plt.colorbar(im2, ax=ax2)

# summary/mean values visualization
summarized_stats.plot(column=f'mean_{variable}_2015', scheme='quantiles', k=5, cmap='YlOrRd', legend=True,
    legend_kwds={'loc': 'lower left', 'title': f'mean {variable}'}, linewidth=0.5, ax=ax3,
    missing_kwds={'color': 'lightgrey', 'label': 'No Data'}
)
ax3.set_title(f'mean {variable} per census tract 2015')
ax3.axis('off')

summarized_stats.plot(column=f'mean_{variable}_2025', scheme='quantiles', k=5, cmap='YlOrRd', legend=True,
    legend_kwds={'loc': 'lower left', 'title': f'mean {variable}'}, linewidth=0.5, ax=ax4,
    missing_kwds={'color': 'lightgrey', 'label': 'No Data'}
)
ax4.set_title(f'mean {variable} per census tract 2025')
ax4.axis('off')

plt.tight_layout()
plt.show()