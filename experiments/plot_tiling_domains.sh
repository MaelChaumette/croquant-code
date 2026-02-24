#!/bin/bash


# This script can be used to reproduce Figure 4.2 in ...
# It shows the two types of tiling domains depending on the size of the vector.


########## To change if not using default parameters ##########
size=2
bit=3
delta=5
save_img_dir="results/tiling_domains"
###############################################################


python3 src/scripts/plot_function.py \
    --function plot_one_tiling_domain \
    --n $size \
    --bit $bit \
    --delta $delta \
    --seed 123 \
    --save_img_dir $save_img_dir \
    --draw_zoom False


python3 src/scripts/plot_function.py \
    --function plot_one_tiling_domain \
    --n 1 \
    --bit $bit \
    --delta $delta \
    --seed 123 \
    --save_img_dir $save_img_dir \
    --draw_zoom False