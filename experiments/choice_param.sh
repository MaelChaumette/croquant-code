#!/bin/bash

# This script can be used to reproduce Figure 5.2 in ...
# It computes the evolution of the gain in quantization error in terms of the gain in time
# when varying the parameters delta, m, n and the distribution of the components of the vectors.


########## To change if not using pre-computed results ##########
bit=4
max_points=100
save_dir="results/choice_param_bit=${bit}"
save_img_dir="results/choice_param_bit=${bit}"
#################################################################

########## Uncomment the following lines to recompute results from scratch ##########
# for delta in 0 1 2 3 4 5 6 7 8
# do
#     for distrib in "uniform" "normal" "roots_of_unity" "finite_alphabet"
#     do
#         for n in 2 32
#         do
#             for m in 2 32
#             do

#                 python3 src/scripts/compare_error_time.py \
#                     --m $m \
#                     --n $n \
#                     --bit $bit \
#                     --delta $delta \
#                     --distrib $distrib \
#                     --max_points $max_points \
#                     --save_dir "${save_dir}/m=${m}/n=${n}/distrib=${distrib}/delta=${delta}"
#             done
#         done
#     done
# done

python3 src/scripts/plot_choice_param.py \
    --save_dir $save_dir \
    --save_img_dir $save_img_dir