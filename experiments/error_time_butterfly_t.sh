#!/bin/bash


# This script can be used to reproduce Figure 6.1 (left) in ...
# It computes the evolution of the quantization error in terms of the number of significand mantissa bits for random butterfly matrices.


########## To change if not using pre-computed results ##########
size=256
delta=2
max_points=10
save_dir="results/error_time_butterfly_t_size=${size}_delta=${delta}"
save_img_dir="results/error_time_butterfly_t_size=${size}_delta=${delta}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for bit in 2 3 4 5 6 7
# do
#     python3 src/scripts/compare_error_time_butterfly.py \
#         --n $size \
#         --bit $bit \
#         --delta $delta \
#         --max_points $max_points \
#         --save_dir "${save_dir}/bit=${bit}"
# done

python3 src/scripts/plot_error_time_butterfly.py \
    --function plot_butterfly_quantization_error_t \
    --n $size \
    --delta $delta \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir