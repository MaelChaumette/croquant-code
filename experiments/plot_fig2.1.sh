#!/bin/bash


# This script can be used to reproduce Figure 2.1 in ...
# It shows:
#   1. two potential tiling domains,
#   2. the tiling domain that takes into account the geometry of the problem,
#   3. a zoom on the accumulation phenomenon.


########## To change if not using default parameters ##########
size=2
bit=3
delta=5
save_img_dir="results/fig2.1"
###############################################################


python3 src/scripts/plot_function.py \
    --function plot_compare_tiling_domains \
    --n $size \
    --bit $bit \
    --seed 123 \
    --save_img_dir $save_img_dir


python3 src/scripts/plot_function.py \
    --function plot_one_tiling_domain \
    --n $size \
    --bit $bit \
    --delta $delta \
    --seed 123 \
    --save_img_dir $save_img_dir \
    --draw_zoom True