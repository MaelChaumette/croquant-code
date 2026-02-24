#!/bin/bash


# This script can be used to reproduce Figure 6.1 (right) in ...
# It computes the evolution of the quantization error in terms of the size of the butterfly matrices.


########## To change if not using pre-computed results ##########
bit=4
delta=2
max_points=10
save_dir="results/error_time_butterfly_n_bit=${bit}_delta=${delta}"
save_img_dir="results/error_time_butterfly_n_bit=${bit}_delta=${delta}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for size in 16 32 64 128 256 512 1024
# do
#     python3 src/scripts/compare_error_time_butterfly.py \
#         --n $size \
#         --bit $bit \
#         --delta $delta \
#         --max_points $max_points \
#         --save_dir "${save_dir}/size=${size}"
# done

python3 src/scripts/plot_error_time_butterfly.py \
    --function plot_butterfly_quantization_error_n \
    --bit $bit \
    --delta $delta \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir