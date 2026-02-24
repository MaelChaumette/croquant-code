#!/bin/bash


# This script can be used to reproduce Figure 5.1 in ...
# It computes the distribution of the quantization error


########## To change if not using pre-computed results ##########
bit=4
delta=8
max_points=100
save_dir="results/error_per_delta_bit=${bit}_delta=${delta}"
save_img_dir="results/error_per_delta_bit=${bit}_delta=${delta}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for distrib in "uniform" "normal" "roots_of_unity" "finite_alphabet"
# do
#     for m in 2 32
#     do
#         for n in 2 32
#         do
#         python3 src/scripts/search_beyond_acc.py \
#             --m $m \
#             --n $n \
#             --bit $bit \
#             --delta $delta \
#             --distrib $distrib \
#             --save_dir "${save_dir}/m=${m}/n=${n}/distrib=${distrib}"
#         done
#     done
# done

python3 src/scripts/plot_search_beyond_acc.py \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir