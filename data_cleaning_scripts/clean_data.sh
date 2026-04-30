#!/bin/bash
set -e 

echo "!! IMPORTANT !! Close any python visualization windows to continue running the processing files"

echo "Cleaning the Variable: Number of Extreme Heat Days"
python3 extreme_heat_days.py

echo "Clipping PRISM rasters to DC boundaries and stacking all month bands"
python3 clip_prisms.py tdmean
python3 clip_prisms.py tmax

echo "Cleaning the Variable: tdmean"
python3 average_zonal_stats.py tdmean

echo "Cleaning the Variable: tmax"
python3 average_zonal_stats.py tmax

echo "Cleaning the Variable: green spaces (Percent Impervious Surface)"
python3 green_spaces.py

echo "Cleaning the demographics variables"
python3 demographics.py

echo "Success! All variables were cleaned and are available in <filepath TBD>"