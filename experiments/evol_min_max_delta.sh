#!/bin/bash


#########################################
######### UNUSED IN THE ARTICLE #########
#########################################


# This script can be used to see the evolution of the computation time in terms of min(m, n), max(m, n) and \delta.


########## To change if not using pre-computed results ##########
bit=4
delta=2
max_points=100
distrib="unif"
save_dir="results/unused"
save_img_dir="results/unused"
#################################################################


########## Uncomment the following lines to recompute results from scratch ##########
# # Evolution of the time in terms of min(m, n)
# for m in 32 256 1024
# do
#     for n in 4 8 12 16 20 24 28 32
#     do
#     python3 src/scripts/compare_error_time.py \
#         --m $m \
#         --n $n \
#         --bit $bit \
#         --delta $delta \
#         --distrib $distrib \
#         --max_points $max_points \
#         --save_dir "${save_dir}/evol_time_min_bit=${bit}_delta=${delta}/m=${m}/n=${n}"
#     done
# done

python3 src/scripts/plot_evol_time_min_max.py \
    --function plot_time_min \
    --save_dir ${save_dir}/evol_time_min_bit=${bit}_delta=${delta} \
    --save_img_dir ${save_img_dir}/evol_time_min_bit=${bit}_delta=${delta}

########## Uncomment the following lines to recompute results from scratch ##########
# # Evolution of the time in terms of max(m, n)
# for m in 2 4 8
# do
#     for n in 100 200 300 400 500 600 700 800 900 1000
#     do
#     python3 src/scripts/compare_error_time.py \
#         --m $m \
#         --n $n \
#         --bit $bit \
#         --delta $delta \
#         --distrib $distrib \
#         --max_points $max_points \
#         --save_dir "${save_dir}/evol_time_max_bit=${bit}_delta=${delta}/m=${m}/n=${n}"
#     done
# done

python3 src/scripts/plot_evol_time_min_max.py \
    --function plot_time_max \
    --save_dir ${save_dir}/evol_time_max_bit=${bit}_delta=${delta} \
    --save_img_dir ${save_img_dir}/evol_time_max_bit=${bit}_delta=${delta}

########## Uncomment the following lines to recompute results from scratch ##########
# # Evolution of the time in terms of \delta
# for n in 2 4 8
# do
#     for delta in 1 2 3 4 5 6 7 8 9 10
#     do
#         python3 src/scripts/compare_error_time.py \
#             --m $n \
#             --n $n \
#             --bit $bit \
#             --delta $delta \
#             --distrib $distrib \
#             --max_points $max_points \
#             --save_dir "${save_dir}/evol_time_delta_bit=${bit}/n=${n}/delta=${delta}"
#     done
# done

python3 src/scripts/plot_evol_time_min_max.py \
    --function plot_time_delta \
    --bit $bit \
    --save_dir ${save_dir}/evol_time_delta_bit=${bit} \
    --save_img_dir ${save_img_dir}/evol_time_delta_bit=${bit}
