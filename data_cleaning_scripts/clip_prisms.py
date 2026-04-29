import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import subprocess
import sys

# -------------------- Purpose -------------------- # 
# Stacks all of the rasters for 2015 and 2025 over all months into 2 stacked
# .tif's (for 2015 and 2025), then clips both of those to the DC boundaries so the data is much smaller

# ------------------ Requirements ----------------- #
# Takes in exactly 1 command line arguments: the variable you are clipping. Possible choices: ['tdmean', 'tmax']


# Load command line arguments
if(len(sys.argv) != 2):
    print('''Incorrect number of command line arguments!
Exactly 1 argument is required: the variable you are clipping. The possible choices are: tdmean OR tmax.
Please run either:
    python3 clip_prisms.py tdmean  OR
    python3 clip_prisms.py tmax''')
    sys.exit(0)
    
# Note to self: sys.argv[0] -> program called, ignore this
variable = str(sys.argv[1])

# Load DC boundaries
dc_bounds = gpd.read_file('../data/DC_Boundary_shapefile/DC_Boundary.shp')
# temporarily reproject to the CRS of the rasters to clip
dc_bounds.to_crs('EPSG:4269', inplace=True)


#####################################
# Since the steps for 2015 and 2025 are similar, define a function that will be run twice for both years
def clip_prisms_by_year(year: str):

    # find all month bands using glob
    all_months = sorted(glob(f'../data/{variable}/{year}/prism_{variable}_us*.tif'))
    print('found', len(all_months), f'bands for {year}')

    # stack all bands into one mega 6-band file

    # read the profile from the first band and copy + update the profile
    with rasterio.open(all_months[0]) as src0:
        stacked_profile = src0.profile.copy()

    # update profile
    stacked_profile.update({
        'count': len(all_months)
    })

    # stack bands into a master file with all bands from each month
    print(f'stacking {year} rasters')
    with rasterio.open(f'../data/{variable}/{year}/{variable}_months_stacked_{year}.tif', 'w', **stacked_profile) as dst:
        for band_num, filename in enumerate(all_months, start=1):
            with rasterio.open(filename) as src:
                dst.write(src.read(1), band_num)

    # now clip the stacked 6-band file to the DC boundaries
    print(f'clipping {year} rasters to DC boundaries')
    with rasterio.open(f'../data/{variable}/{year}/{variable}_months_stacked_{year}.tif') as src:
        # Guide to using clip() on a raster:
        # https://gis.stackexchange.com/questions/444062/clipping-raster-geotiff-with-a-vector-shapefile-in-python
        out_image, out_transform = mask(src, dc_bounds.geometry, crop=True)
        clipped_profile = src.meta.copy()
        
    clipped_profile.update({
        'driver': 'Gtiff',
        'height': out_image.shape[1],
        'width': out_image.shape[2],
        'transform': out_transform
    })
    
    # write to the final clipped output file
    with rasterio.open(f'../data/{variable}/{year}/{variable}_months_stacked_clipped_{year}.tif', 'w', **clipped_profile) as dst:
        dst.write(out_image)


#####################################
# Run the above function for both years
clip_prisms_by_year('2015')
clip_prisms_by_year('2025')


#####################################
# visualize the final images

# Re-open both final rasters to read the data
with rasterio.open(f'../data/{variable}/2015/{variable}_months_stacked_clipped_2015.tif') as src:
    # read the data and convert it to float + np.nan as nodata to display
    prism_data_2015 = src.read(1)
    prism_data_2015.astype(np.float32)
    prism_data_2015[prism_data_2015 == -9999] = np.nan

with rasterio.open(f'../data/{variable}/2025/{variable}_months_stacked_clipped_2025.tif') as src:
    # read the data and convert it to float + np.nan as nodata to display
    prism_data_2025 = src.read(1)
    prism_data_2025.astype(np.float32)
    prism_data_2025[prism_data_2025 == -9999] = np.nan

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

im1 = ax1.imshow(prism_data_2015, cmap='Greens')
ax1.set_title(f'2015 {variable}')
plt.colorbar(im1, ax=ax1)

im2 = ax2.imshow(prism_data_2025, cmap='Greens')
ax2.set_title(f'2025 {variable}')
plt.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()