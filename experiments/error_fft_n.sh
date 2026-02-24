#!/bin/bash


# This script can be used to reproduce Figure 6.2 (right) in ...
# It computes the evolution of the FFT error in terms of of the size of the matrix


########## To change if not using pre-computed results ##########
bit=4
delta=2
max_points=100
save_dir="results/error_fft_n_bit=${bit}_delta=${delta}"
save_img_dir="results/error_fft_n_bit=${bit}_delta=${delta}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for size in 16 32 64 128 256 512 1024
# do
#     python3 src/scripts/compare_error_fft.py \
#         --n $size \
#         --bit $bit \
#         --delta $delta \
#         --max_points $max_points \
#         --save_dir "${save_dir}/size=${size}"
# done

python3 src/scripts/plot_error_fft.py \
    --function plot_error_fft_n \
    --bit $bit \
    --delta $delta \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir