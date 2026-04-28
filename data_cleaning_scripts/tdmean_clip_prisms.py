import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import subprocess

# -------------------- Purpose -------------------- # 
# Stacks all of the rasters for tdmean for 2015 and 2025 over all months into 2 stacked
# .tif's (for 2015 and 2025), then clips both of those to the DC boundaries so the data is much smaller

# Load DC boundaries
dc_bounds = gpd.read_file('../data/DC_Boundary_shapefile/DC_Boundary.shp')
# temporarily reproject to the CRS of the rasters to clip
dc_bounds.to_crs('EPSG:4269', inplace=True)


# ------- 2015 ------- #

# find all month bands using glob
all_months_2015 = sorted(glob('../data/tdmean/2015/prism_tdmean_us*.tif'))
print('found', len(all_months_2015), 'bands for 2015')

# stack all bands into one mega 6-band file

# read the profile from the first band and copy + update the profile
with rasterio.open(all_months_2015[0]) as src0:
    stacked_profile = src0.profile.copy()

# update profile
stacked_profile.update({
    'count': len(all_months_2015)
})

# stack bands into a master file (tdmean_months_stacked_2015.tif)
print('stacking 2015 rasters')
with rasterio.open('../data/tdmean/2015/tdmean_months_stacked_2015.tif', 'w', **stacked_profile) as dst:
    for band_num, filename in enumerate(all_months_2015, start=1):
        with rasterio.open(filename) as src:
            dst.write(src.read(1), band_num)

# now clip the stacked 6-band file to the DC boundaries
print('clipping 2015 rasters to DC boundaries')
with rasterio.open('../data/tdmean/2015/tdmean_months_stacked_2015.tif') as src:
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
              
with rasterio.open('../data/tdmean/2015/tdmean_months_stacked_clipped_2015.tif', 'w', **clipped_profile) as dst:
    dst.write(out_image)



# ------- 2025 ------- #

# find all month bands using glob
all_months_2025 = sorted(glob('../data/tdmean/2025/prism_tdmean_us*.tif'))
print('found', len(all_months_2025), 'bands for 2025')

# stack all bands into one mega 6-band file

# read the profile from the first band and copy + update the profile
with rasterio.open(all_months_2025[0]) as src0:
    stacked_profile = src0.profile.copy()

# update profile
stacked_profile.update({
    'count': len(all_months_2025)
})

# stack bands into a master file (tdmean_months_stacked_2025.tif)
print('stacking 2025 rasters')
with rasterio.open('../data/tdmean/2025/tdmean_months_stacked_2025.tif', 'w', **stacked_profile) as dst:
    for band_num, filename in enumerate(all_months_2025, start=1):
        with rasterio.open(filename) as src:
            dst.write(src.read(1), band_num)

# now clip the stacked 6-band file to the DC boundaries
print('clipping 2025 rasters to DC boundaries')
with rasterio.open('../data/tdmean/2025/tdmean_months_stacked_2025.tif') as src:
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
              
with rasterio.open('../data/tdmean/2025/tdmean_months_stacked_clipped_2025.tif', 'w', **clipped_profile) as dst:
    dst.write(out_image)


#####################################
# visualize the final images

# Re-open both final rasters to read the data
with rasterio.open('../data/tdmean/2015/tdmean_months_stacked_clipped_2015.tif') as src:
    # read the data and convert it to float + np.nan as nodata to display
    prism_data_2015 = src.read(1)
    prism_data_2015.astype(np.float32)
    prism_data_2015[prism_data_2015 == -9999] = np.nan

with rasterio.open('../data/tdmean/2025/tdmean_months_stacked_clipped_2025.tif') as src:
    # read the data and convert it to float + np.nan as nodata to display
    prism_data_2025 = src.read(1)
    prism_data_2025.astype(np.float32)
    prism_data_2025[prism_data_2025 == -9999] = np.nan

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

im1 = ax1.imshow(prism_data_2015, cmap='Greens')
ax1.set_title('2015 tdmean')
plt.colorbar(im1, ax=ax1)

im2 = ax2.imshow(prism_data_2025, cmap='Greens')
ax2.set_title('2025 tdmean')
plt.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()