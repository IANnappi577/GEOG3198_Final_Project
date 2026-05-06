import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import PROJECTION

# -------------------- Purpose -------------------- # 
# Load census demographic variables, and clean and clip them to the correct
# tigerline shapefiles

# -------------------- Outputs -------------------- # 
# Final cleaned census variables available in data/demographic_data/final_tables

# Create a function to perform the same steps on both 2015 and 2025 census data.
def process_demographics_data(year: str):
    
    # Load all the raw census tables
    tot_pop = pd.read_csv(f'../data/demographic_data/raw_tables/{year}_B01003.csv')
    disability_poverty = pd.read_csv(f'../data/demographic_data/raw_tables/{year}_B17020_B18101.csv')

    # Load the tigerline census tracts
    census_bounds = gpd.read_file(f'../data/tigerline_shapefiles/tigerline_{year}_tract/tl_{year}_11_tract.shp')
    # Reproject to the final projection
    census_bounds.to_crs(PROJECTION, inplace=True)

    # Drop the unnecessary columns (blank or unneeded)
    cols = ['GISJOIN', 'STUSAB', 'REGIONA', 'DIVISIONA', 'STATE', 'STATEA', 'COUNTY', 'COUNTYA',
        'COUSUBA', 'PLACEA', 'TRACTA', 'CONCITA', 'AIANHHA', 'RES_ONLYA', 'TRUSTA', 'AIHHTLI', 
        'ANRCA', 'CBSAA', 'CSAA', 'METDIVA', 'UAA', 'CDCURRA', 'SLDUA', 'SLDLA', 'ZCTA5A', 'SUBMCDA',
        'SDELMA', 'SDSECA', 'SDUNIA', 'PCI', 'PUMAA', 'BTTRA', 'NAME_E', 'NAME_M']
    disability_poverty.drop(columns=cols, inplace=True)
    tot_pop.drop(columns=cols, inplace=True)
    
    # Drop columns NOT found in disability_poverty
    tot_pop.drop(columns=['BLKGRPA', 'BTBGA'], inplace=True)

    # drop columns specific to 2015 data
    if(year == '2015'):
        extra_cols = ['AITSCEA', 'NECTAA', 'CNECTAA', 'NECTADIVA']
        disability_poverty.drop(columns=extra_cols, inplace=True)
        tot_pop.drop(columns=extra_cols, inplace=True)

    # drop columns specific to 2025 data
    if(year == '2025'):
        disability_poverty.drop(columns=['AITSA'], inplace=True)
        tot_pop.drop(columns=['AITSA'], inplace=True)

    # Clean the GEOID that can be joined to the census tracts
    # This value is different for 2015 and 2025, of course, cause the census bureau likes changing
    # things between years.
    if(year == '2015'):
        # For 2015, we need to convert the GEOID column into one compatible with the Tigerline shapefile GEOID
        # Simple drop the prefix '14000US' from the GEOID column
        tot_pop['GEOID_JOIN'] = [geoid[7:] for geoid in tot_pop['GEOID']]
        disability_poverty['GEOID_JOIN'] = [geoid[7:] for geoid in disability_poverty['GEOID']]
        # also drop the old confusing 'GEOID' column in these so it doesn't cause problems while merging
        tot_pop.drop(columns=['GEOID'], inplace=True)
        disability_poverty.drop(columns=['GEOID'], inplace=True)
    else:
        # For 2025, we simply need to rename the TL_GEO_ID to be the GEOID_JOIN column to join on
        tot_pop.rename(columns={'TL_GEO_ID': 'GEOID_JOIN'}, inplace=True)
        disability_poverty.rename(columns={'TL_GEO_ID': 'GEOID_JOIN'}, inplace=True)
        # Also change this column to a string, as it is currently an int64 and cannot be joined to the string GEOID:
        tot_pop['GEOID_JOIN'] = tot_pop['GEOID_JOIN'].astype(str)
        disability_poverty['GEOID_JOIN'] = disability_poverty['GEOID_JOIN'].astype(str)

    # Join both tables to the census tracts
    dem_stats = pd.merge(census_bounds, tot_pop, how='inner', left_on='GEOID', right_on='GEOID_JOIN')
    # drop some columns that will be duplicated when we join the second table
    dem_stats.drop(columns=['GEOID_JOIN', 'YEAR'], inplace=True)
    # join second table
    dem_stats = pd.merge(dem_stats, disability_poverty, how='inner', left_on='GEOID', right_on='GEOID_JOIN')

    # Now calculate the variables we want and put them in appropriatly-named columns

    # The census bureau official column names follow a pre-determined pattern, where a 4-character prefix representing 
    # the year is followed by the variable number code ('E' + a 3-digit number). Although the prefix differs by year, the 
    # variable codes are the same, so we will dynamically build the column names per year. So, we define the prefix for each 
    # year, and will substitute this to form the complete column name:
    if(year == '2015'):
        prefix = 'AD2S'
    else:
        prefix = 'AU9J'

    # When fetching and computing each of the variables below, each column is normalized by the total population
    # column, either AD2SE001 for 2015 and AU9JE001 for 2025.
    # See the Data Sources document or the official codebooks in ../data/demographic_data/raw_tables/ to see what each 
    # column code means.

    # Finally, each final value is a decimal percentage, so to get the percentage on a scale from 0-100,
    # simply multiply by 100

    # ------------
    # Percentage of Individuals under the age of 5
    #       --> Sum the number of male and female individuals < 5
    dem_stats['Perc_un_5'] = (dem_stats[prefix + 'E003'] + dem_stats[prefix + 'E022']) / dem_stats[prefix + 'E001']
    # print(dem_stats['Perc_un_5'].head(5))

    # ------------
    # Percentage of Elderly Individuals over 65
    #       --> Sum the number of male and female individuals in the 65-74 and 75+ categories
    dem_stats['Perc_ov_65'] = (dem_stats[prefix + 'E015'] + dem_stats[prefix + 'E018'] +
                                dem_stats[prefix + 'E034'] + dem_stats[prefix + 'E037']) / dem_stats[prefix + 'E001']
    # print(dem_stats['Perc_ov_65'].head(5))

    # ------------
    # Percentage of Individuals with a Disability
    #       --> Sum the number of male and female individuals with a disability in every age category                                 
    dem_stats['Perc_disabl'] = (dem_stats[prefix + 'E004'] + dem_stats[prefix + 'E007'] +
                                dem_stats[prefix + 'E010'] + dem_stats[prefix + 'E013'] +
                                dem_stats[prefix + 'E016'] + dem_stats[prefix + 'E019'] +
                                dem_stats[prefix + 'E023'] + dem_stats[prefix + 'E026'] +
                                dem_stats[prefix + 'E029'] + dem_stats[prefix + 'E032'] +
                                dem_stats[prefix + 'E035'] + dem_stats[prefix + 'E038']) / dem_stats[prefix + 'E001']
    # print(dem_stats['Perc_disabl'].head(5))

    # Now the other table (For poverty statistics) has a different prefix for 2015 and 2025, so update the prefix:
    if(year == '2015'):
        prefix = 'AD2D'
    else:
        prefix = 'AU84'

    # ------------
    # Percentage of Individuals Below the Poverty Level
    #       --> Simply total number of individuals under the poverty level, normalized by the number of
    #               people in this survey
    dem_stats['Perc_in_pov'] = dem_stats[prefix + 'E002'] / dem_stats[prefix + 'E001']
    # print(dem_stats['Perc_in_pov'].head(5))

    # Remove the unneeded columns and only keep the columns we calculated for export
    final_statistics = dem_stats[['GEOID', 'NAME', 'ALAND', 'AWATER', 'Perc_un_5', 'Perc_ov_65', 
                    'Perc_disabl', 'Perc_in_pov', 'geometry']].copy()
    print(final_statistics.head(5))

    # Export the final geojson
    final_statistics.to_file(f'../data/demographic_data/final_tables/{year}_final_stats.geojson')


#####################################
# Run the above function for both years
print('-------- 2015 demographics --------')
process_demographics_data('2015')
print()

print('-------- 2025 demographics --------')
process_demographics_data('2025')