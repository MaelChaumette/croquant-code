# Code for reproducible research - "CROQuant: Complex Rank-One Quantization Algorithm, with Application to Butterfly Factorizations"

In the interest of reproducible research, we provide code to reproduce experiments in "[CROQuant: Complex Rank-One Quantization Algorithm, with Application to Butterfly Factorizations](https://hal.science/hal-05520926)" (Maël Chaumette, Rémi Gribonval, Elisa Riccietti).

## Getting started
Follow these steps to set up the project environment:
1. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv your_env_name
    ```
2. Activate the virtual environment:
    ```bash
    source your_env_name/bin/activate
    ```
3. Install the source code with the following command:
    ```bash
    pip install -e .
    ```

To deactivate the virtual environment, simply run:
```bash
deactivate
```

## Reproduction of results
We now describe the scripts to reproduce the different results presented in the paper.

### Figure 2.1: Two potential tiling domains with a zoom on the one that we use in our method and a zoom on the accumulation phenomenon
To reproduce Figure 2.1, you simply have to run the following command:
```
bash experiments/plot_fig2.1.sh
```
but you can also change the parameters:
* Different sizes are possible for the input vectors, e.g., `size=2`.
* Different bit allocations are possible, e.g., `bit=3`.
* You can choose your own directory to save the results.

*Time on my machine*: 3 minutes


### Figure 4.1: Impact of the parameter $e$ on the breaklines and the stable regions that intersect the tiling domain
To reproduce Figure 4.1, you simply have to run the following command:
```
bash experiments/plot_impact_e.sh
```
but you can also change the parameters:
* Different sizes are possible for the input vectors, e.g., `size=2`.
* Different bit allocations are possible, e.g., `bit=3`.
* You can choose your own directory to save the results.

*Time on my machine*: 5 seconds


### Figure 4.2: Two types of tiling domains depending on the size of the input vector
To reproduce Figure 4.2, you simply have to run the following command:
```
bash experiments/plot_tiling_domains.sh
```
but you can also change the parameters:
* Different sizes are possible for the input vectors, e.g., `size=2`.
* Different bit allocations are possible, e.g., `bit=3`.

*Time on my machine*: 1 minutes 20 seconds


### Table 5.1: Proportion of couples $(x, y, t)$ that do not satisfy the non-degeneracy assumption (see Definition 3.1)
To reproduce Table 5.1, you simply have to run the following command:
```
bash experiments/verify_assumption.sh
```
but you can also change the parameters:
* Different bit allocations are possible, e.g., `bit=4`.
* Different values for the parameter `delta`, e.g., `delta=2`.
* Different distributions for the input vectors: change distribution names at line 15 of the script ``experiments/verify_assumption.sh``.
* Different sizes are possible for the input vectors: change `m` and `n` values at lines 17 and 19 of the script ``experiments/verify_assumption.sh``.

*Time on my machine* with the pre-defined parameters in the script: 45 seconds per point and per distribution, resulting in **12 hours 30 minutes** per distribution for 1000 points.


### Figure 5.1: Distribution of the error in terms of the parameter $\delta$

#### Use pre-computed results
To reproduce Figure 5.1 using pre-computed results, you simply have to run the following command:
```
bash experiments/search_beyond_acc.sh
```

*Time on my machine*: 24 seconds

#### Recompute results from scratch
To reproduce Figure 5.1 by recomputing the results from scratch, you have to:

1. uncomment lines 17-32 of the script ``experiments/search_beyond_acc.sh``
2. Set the desired `save_dir` and `save_img_dir`
3. Choose your own parameters:
    * The different sizes for the vectors `m` and `n`
    * The number of significand mantissa bits `bit`
    * The different distributions for the input vectors
    * The different values for the parameter `delta`
4. Run `bash experiments/search_beyond_acc.sh`.

*Time on my machine* with the pre-defined parameters in the script: 1 hours 40 minutes per distribution.


### Figure 5.2: Evolution of the the gain in quantization error in terms of the gain in time

#### Use pre-computed results
To reproduce Figure 5.2 using pre-computed results, you simply have to run the following command:
```
bash experiments/choice_param.sh
```

*Time on my machine*: 4 seconds

#### Recompute results from scratch
To reproduce Figure 5.2 by recomputing the results from scratch, you have to:
1. uncomment lines 16-36 of the script ``experiments/choice_param.sh``
2. Set the desired `save_dir` and `save_img_dir`
3. Choose your own parameters:
    * The different sizes for the vectors `m` and `n`
    * The number of significand mantissa bits `bit`
    * The different distributions for the input vectors
    * The different values for the parameter `delta`
4. Run `bash experiments/choice_param.sh`.

*Time on my machine* with the pre-defined parameters in the script: 1 hours 45 minutes for all `delta` values per point and per distribution, resulting in **7 days** per distribution for 100 points.


### Figure 6.1: Evolution of the quantization error in terms the number of mantissa bits and the size of the butterfly matrices

#### Use pre-computed results
To reproduce Figure 6.1 using pre-computed results, you simply have to run the following commands:
```
bash experiments/error_time_butterfly_t.sh
bash experiments/error_time_butterfly_n.sh
```

*Time on my machine*
 - For `experiments/error_time_butterfly_t.sh`: 5 seconds
 - For `experiments/error_time_butterfly_n.sh`: 4 seconds

#### Recompute results from scratch
To reproduce Figure 6.1 by recomputing the results from scratch, you have to:
1. uncomment lines 17-25 of the script ``experiments/error_time_butterfly_t.sh``
2. uncomment lines 17-25 of the script ``experiments/error_time_butterfly_n.sh``
3. Set the desired `save_dir` and `save_img_dir` in both scripts
4. Choose your own parameters:
    * The different sizes for the butterfly matrices
    * The number of significand mantissa bits `bit`
5. Run the two bash scripts `bash experiments/error_time_butterfly_t.sh` and `bash experiments/error_time_butterfly_n.sh`.

*Time on my machine* with the pre-defined parameters in the scripts:
- For `experiments/error_time_butterfly_t.sh`: 12 hours 30 minutes for all `bit` values per point, resulting in **5 days** for 10 points.
- For `experiments/error_time_butterfly_n.sh`: 2 hours 17 minutes for all `n` values per point, resulting in **23 hours** for 10 points.

### Figure 6.2: Evolution of the FFT error in terms the number of mantissa bits and the size of the butterfly matrices

#### Use pre-computed results
To reproduce Figure 6.2 using pre-computed results, you simply have to run the following commands:
```
bash experiments/error_fft_t.sh
bash experiments/error_fft_n.sh
```

*Time on my machine*
 - For `experiments/error_fft_t.sh`: 4 seconds
 - For `experiments/error_fft_n.sh`: 4 seconds

#### Recompute results from scratch
To reproduce Figure 6.2 by recomputing the results from scratch, you have to:
1. uncomment lines 17-25 of the script ``experiments/error_fft_t.sh``
2. uncomment lines 17-25 of the script ``experiments/error_fft_n.sh``
3. Set the desired `save_dir` and `save_img_dir` in both scripts
4. Choose your own parameters:
    * The different sizes for the butterfly matrices
    * The number of significand mantissa bits `bit`
5. Run the two bash scripts `bash experiments/error_fft_t.sh` and `bash experiments/error_fft_n.sh`.

*Time on my machine* with the pre-defined parameters in the scripts:
- For `experiments/error_fft_t.sh`: 3 hours
- For `experiments/error_fft_n.sh`: 30 minutes


### Additional Results
Three additional results can be produced that are not presented in the paper:
the evolution of the computation time of our algorithm in terms of $\min(m, n)$, $\max(m, n)$ and $\delta$.

#### Use pre-computed results
To reproduce these additional results using pre-computed results, you simply have to run the following commands:
```
bash experiments/evol_min_max_delta.sh
```

*Time on my machine*: 10 seconds

#### Recompute results from scratch
To reproduce these additional results by recomputing the results from scratch, you have to:
1. uncomment lines 22-35, 43-56 and 64-77 of the script ``experiments/evol_min_max_delta.sh``
2. Set the desired `save_dir` and `save_img_dir` in the script
3. Choose your own parameters:
    * The different sizes for the vectors `m` and `n`
    * The number of significand mantissa bits `bit`
    * The different values for the parameter `delta`
    * The distribution for the input vectors
4. Run the bash script `bash experiments/evol_min_max_delta.sh`.

*Time on my machine* with the pre-defined parameters in the script:
 - For the evolution in terms of $min(m, n)$: 39 minutes for all `m`, `n` values per point, resulting in **2 days 16 hours** for 100 points.
 - For the evolution in terms of $max(m, n)$: 1 minutes 20 seconds for all `m`, `n` values per point, resulting in **2 hours 14 minutes** for 100 points.
 - For the evolution in terms of `delta`: 4 minutes for all `n` and `delta` values per point, resulting in **7 hours** for 100 points.

## License
CROQuant is released under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) license.

## Citation
```
@unpublished{chaumette:hal-05520926,
  TITLE = {{CROQuant: Complex Rank-One Quantization Algorithm, with Application to Butterfly Factorizations}},
  AUTHOR = {Chaumette, Ma{\"e}l and Gribonval, R{\'e}mi and Riccietti, Elisa},
  URL = {https://hal.science/hal-05520926},
  NOTE = {working paper or preprint},
  YEAR = {2026},
  MONTH = Feb,
  KEYWORDS = {Low-precision Quantization ; Rank-One matrices ; Butterfly matrices ; Fast Fourier transform ; Discrete optimization ; Computations on matrices},
  PDF = {https://hal.science/hal-05520926v1/file/croquant.pdf},
  HAL_ID = {hal-05520926},
  HAL_VERSION = {v1},
}
```