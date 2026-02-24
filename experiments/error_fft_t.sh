#!/bin/bash


# This script can be used to reproduce Figure 6.2 (left) in ...
# It computes the evolution of the FFT error in terms of the number of significand mantissa bits


########## To change if not using pre-computed results ##########
size=256
delta=2
max_points=100
save_dir="results/error_fft_t_size=${size}_delta=${delta}"
save_img_dir="results/error_fft_t_size=${size}_delta=${delta}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for bit in 2 3 4 5 6 7
# do
#     python3 src/scripts/compare_error_fft.py \
#         --n $size \
#         --bit $bit \
#         --delta $delta \
#         --max_points $max_points \
#         --save_dir "${save_dir}/bit=${bit}"
# done

python3 src/scripts/plot_error_fft.py \
    --function plot_error_fft_t \
    --n $size \
    --delta $delta \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir