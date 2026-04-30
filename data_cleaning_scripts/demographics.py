import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import PROJECTION

# -------------------- Purpose -------------------- # 
# Load census demographic variables, and clean and clip them to the correct
# tigerline shapefiles

# Create a function to perform the same steps on both 2015 and 2025 census data.
# Unfortunately, column names for the census csvs are differnet per year. So make
# a dictionary of column names for each year to be able to reuse the same steps in the
# below function

###### NOTE FOR REFACTORING: THE SAME CODE IS USED JUST A DIFFERENT PREFIX: AU9J (2025) vs AD2S (2015)
##### We can do a dynamic substitution instead of this nonsense dictionary scheiß
v_2015 = {
    'Tot_pop': 'AD2SE001',
    'Pop_under_5': ['AD2SE003', 'AD2SE022'],
    'Pop_over_65': ['AD2SE015', 'AD2SE018', 'AD2SE034', 'AD2SE037'],
    'Pop_disabled': ['AD2SE004', 'AD2SE007', 'AD2SE010', 'AD2SE013',
                     'AD2SE016', 'AD2SE019', 'AD2SE023', 'AD2SE026',
                     'AD2SE029', 'AD2SE032', 'AD2SE035', 'AD2SE038'],
    'Tot_Poverty': 'AD2DE001',
    'Pop_in_poverty': 'AD2DE002'
}
v_2025 = {
    'Tot_pop': 'AU9JE001',
    'Pop_under_5': ['AU9JE003', 'AU9JE022'],

    'Pop_over_65': ['AU9JE015', 'AU9JE018', 'AU9JE034', 'AU9JE037'],
    'Pop_disabled': ['AU9JE004', 'AU9JE007', 'AU9JE010', 'AU9JE013',
                     'AU9JE016', 'AU9JE019', 'AU9JE023', 'AU9JE026',
                     'AU9JE029', 'AU9JE032', 'AU9JE035', 'AU9JE038'],
    'Tot_Poverty': 'AU84E001',
    'Pop_in_poverty': 'AU84E002'
}
cen_cols = {
    '2015': v_2015,
    '2025': v_2025
}

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
        'COUSUBA', 'PLACEA', 'TRACTA', 'CONCITA', 'AIANHHA', 'RES_ONLYA', 'TRUSTA', 'AIHHTLI', 'AITSCEA', 
        'ANRCA', 'CBSAA', 'CSAA', 'METDIVA', 'NECTAA', 'CNECTAA', 'NECTADIVA', 'UAA', 'CDCURRA', 'SLDUA', 'SLDLA',
        'ZCTA5A', 'SUBMCDA', 'SDELMA', 'SDSECA', 'SDUNIA', 'PCI', 'PUMAA', 'BTTRA', 'NAME_E', 'NAME_M']
    disability_poverty.drop(columns=cols, inplace=True)
    tot_pop.drop(columns=cols, inplace=True)
    tot_pop.drop(columns=['BLKGRPA', 'BTBGA'], inplace=True)
    census_bounds.drop(columns=['STATEFP', 'COUNTYFP', 'TRACTCE', 'NAMELSAD', 'MTFCC', 'FUNCSTAT', 'INTPTLAT', 'INTPTLON'], inplace=True)

    # clean the GEOID that can be joined to the census tracts
    # drop the prefix '14000US' from the GEOID column
    tot_pop['GEOID_JOIN'] = [geoid[7:] for geoid in tot_pop['GEOID']]
    disability_poverty['GEOID_JOIN'] = [geoid[7:] for geoid in disability_poverty['GEOID']]
    # also drop the old confusing 'GEOID' column in these so it doesn't cause problems while merging
    tot_pop.drop(columns=['GEOID'], inplace=True)
    disability_poverty.drop(columns=['GEOID'], inplace=True)

    # Join both tables to the census tracts
    dem_stats = pd.merge(census_bounds, tot_pop, how='inner', left_on='GEOID', right_on='GEOID_JOIN')
    # drop some columns that will be duplicated when we join the second table
    dem_stats.drop(columns=['GEOID_JOIN', 'YEAR'], inplace=True)
    # join second table
    dem_stats = pd.merge(dem_stats, disability_poverty, how='inner', left_on='GEOID', right_on='GEOID_JOIN')

    # Now calculate the variables we want and put them in appropriatly-named columns
    # Get the column names from the dictionary cen_cols described at the top of the program
    col_n = cen_cols[f'{year}']

    # Each column is normalized by the total population: column AD2SE001 for 2015 and AUO6M001 for 2025
    # See the data sources document to see what each code column means.

    # Each final value is a decimal percentage, so to get the percentage on a scale from 0-100,
    # simply multiply by 100

    # ------------
    # Percentage of Individuals under the age of 5
    #       --> Sum the number of male and female individuals < 5
    dem_stats['Perc_un_5'] = (dem_stats[col_n['Pop_under_5'][0]] + dem_stats[col_n['Pop_under_5'][1]]) / dem_stats[col_n['Tot_pop']]
    # print(dem_stats['Perc_un_5'].head(5))

    # ------------
    # Percentage of Elderly Individuals over 65
    #       --> Sum the number of male and female individuals in the 65-74 and 75+ categories
    dem_stats['Perc_ov_65'] = (dem_stats[col_n['Pop_over_65'][0]] + dem_stats[col_n['Pop_over_65'][1]] +
                                dem_stats[col_n['Pop_over_65'][2]] + dem_stats[col_n['Pop_over_65'][3]]) / dem_stats[col_n['Tot_pop']]
    # print(dem_stats['Perc_ov_65'].head(5))

    # ------------
    # Percentage of Individuals with a Disability
    #       --> Sum the number of male and female individuals with a disability in every age category                            
    dem_stats['Perc_disabl'] = (dem_stats[col_n['Pop_disabled'][0]] + dem_stats[col_n['Pop_disabled'][1]] +
                                dem_stats[col_n['Pop_disabled'][2]] + dem_stats[col_n['Pop_disabled'][3]] +
                                dem_stats[col_n['Pop_disabled'][4]] + dem_stats[col_n['Pop_disabled'][5]] +
                                dem_stats[col_n['Pop_disabled'][6]] + dem_stats[col_n['Pop_disabled'][7]] +
                                dem_stats[col_n['Pop_disabled'][8]] + dem_stats[col_n['Pop_disabled'][9]] +
                                dem_stats[col_n['Pop_disabled'][10]] + dem_stats[col_n['Pop_disabled'][11]]) / dem_stats[col_n['Tot_pop']]
    # print(dem_stats['Perc_disabl'].head(5))

    # ------------
    # Percentage of Individuals Below the Poverty Level
    #       --> Simply total number of individuals under the poverty level, normalized by the number of
    #               people in this survey
    dem_stats['Perc_in_pov'] = dem_stats[col_n['Pop_in_poverty']] / dem_stats[col_n['Tot_Poverty']]
    # print(dem_stats['Perc_in_pov'].head(5))

    # Remove the unneeded columns and only keep the columns we calculated for export
    final_statistics = dem_stats[['GEOID', 'NAME', 'ALAND', 'AWATER', 'Perc_un_5', 'Perc_ov_65', 'Perc_disabl', 'Perc_in_pov', 'geometry']].copy()
    # print(final_statistics.head(5))

    # Export the final geojson
    final_statistics.to_file(f'../data/demographic_data/final_tables/{year}_final_stats.geojson')

process_demographics_data('2015')
#process_demographics_data('2025')
