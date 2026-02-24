#!/bin/bash


# This script can be used to reproduce Table 5.1 in ...
# It computes the proportion of couples (x, y) that does not satisfy the non-degeneracy assumption.


########## To change if not using default parameters ##########
bit=4
max_points=1000
###############################################################


for distrib in "uniform" "normal" "finite_alphabet" "roots_of_unity"
do
    for m in 2 32
    do
        for n in 2 32
        do
        python3 src/scripts/verify_assumption.py \
            --m $m \
            --n $n \
            --bit $bit \
            --distrib $distrib \
            --max_points $max_points
        done
    done
done