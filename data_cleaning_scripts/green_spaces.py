import geopandas as gpd
import pandas as pd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from config import PROJECTION

# -------------------- Purpose -------------------- # 
# Loads and summarizes percentage impervious surface for both 2015 and 2024 across the DC
# census tracts using zonal_stats()

# Define a function to do the same steps for the 2015 and 2024 rasters
def clean_green_space_raster(year: str):
    # Load census tract boundaries
    # Change the year to 2025 if we are processing the 2024 raster:
    if(year == '2024'):
        census_year = '2025'
    else:
        census_year = '2015'
    census_bounds = gpd.read_file(f'../data/tigerline_shapefiles/tigerline_{census_year}_tract/tl_{census_year}_11_tract.shp')

    # Load the percent impervious raster
    with rasterio.open(f'../data/green_areas/NLCD_{year}/Annual_NLCD_Fractional_Impervious_{year}.tiff') as src:

        # reproject the census tracts to the CRS of the raster (custom PROJCS projection)
        census_bounds.to_crs(src.profile['crs'], inplace=True)

        # read the first band (there is only 1 band) and convert nodata values to np.nan
        perc_impervious = src.read(1)
        perc_impervious = perc_impervious.astype(np.float32)
        # the nodata value in our case is 250 (unsigned 8-bit int)
        perc_impervious[perc_impervious == src.profile['nodata']] = np.nan

        # use zonal_stats() to summarize the percent impervious surface per census tract
        # Since the resolution on this raster is much higher than the PRISM data, we can
        # use all_touched=False and still get accurate means
        mean_per_census_tract = zonal_stats(
            vectors=census_bounds,
            raster=perc_impervious,
            nodata=np.nan,
            stats=['mean'],
            affine=src.profile['transform'],
            all_touched=True
        )
        # Convert to a pandas DataFrame
        mean_per_census_tract = pd.DataFrame(mean_per_census_tract)

        # Add the mean to the census tracts dataframe
        census_bounds[f'mean_imperv_{year}'] = mean_per_census_tract['mean']

    # reproject to the target CRS and export the census tract bounds with the new column
    census_bounds.to_crs(PROJECTION, inplace=True)
    census_bounds.to_file(f'../data/green_areas/NLCD_{year}/census_imperv_surface_{year}.geojson')

    # visualize the results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    im1 = ax1.imshow(perc_impervious, cmap='Greens')
    ax1.set_title(f'{year} percent impervious surface')
    plt.colorbar(im1, ax=ax1)

    census_bounds.plot(column=f'mean_imperv_{year}', scheme='natural_breaks', k=5, cmap='YlOrRd', legend=True,
        legend_kwds={'loc': 'lower left', 'title': f'Percent Impervious Surface'}, linewidth=0.5, ax=ax2, edgecolor='black',
        missing_kwds={'color': 'lightgrey', 'label': 'No Data'}
    )
    ax2.set_title(f'Mean Percent Impervious Surface per Census Tract {year}')
    ax2.axis('off')

    plt.tight_layout()
    plt.show()
        

#####################################
# Run the above function for both years
clean_green_space_raster('2015')
clean_green_space_raster('2024')