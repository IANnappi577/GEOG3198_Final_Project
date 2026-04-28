#!/bin/bash
set -e 

echo "Cleaning the Variable: Number of Extreme Heat Days"
python3 extreme_heat_days.py

echo "Clipping PRISM rasters to DC boundaries and stacking all month bands"
echo "Close any python visualization windows to continue processing"
python3 tdmean_clip_prisms.py
python3 tmax_clip_prisms.py

# echo "Cleaning the Variable: tdmean"
# python3 tdmean_zonal_stats.py

# echo "Cleaning the Variable: tmax"
# python3 tmax_zonal_stats.py