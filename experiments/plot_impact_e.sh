#!/bin/bash


# This script can be used to reproduce Figure 4.1 in ...
# It shows the evolution of the breaklines and the stable regions in terms of e.


########## To change if not using default parameters ##########
size=2
bit=3
delta=5
save_img_dir="results/impactE"
###############################################################


python3 src/scripts/plot_function.py \
    --function plot_impact_param \
    --n $size \
    --bit $bit \
    --seed 123 \
    --save_img_dir $save_img_dir