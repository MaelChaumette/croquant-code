import numpy as np

from src.complex_case import (
    c,
    chop_complex,
    stochastic_chop_complex,
    fixed_chop_complex,
    get_centroids_accum,
    generate_midpoints,
    generate_directions,
    get_centroids,
    find_e_max,
    find_e_min,
    normalize_direction_set
)
from src.borders import build_tiling_domain


def _find_xy_complex(x, normalized_direction_set, y, tx, ty, border, delta):
    x_approx, y_approx = np.zeros_like(x), np.zeros_like(y)
    lbd_approx, mu_approx = 0, 0
    old_c = c(x, y, x_approx, y_approx)

    centroids_accum = get_centroids_accum(normalized_direction_set, tx, border)
    e_max = find_e_max(normalized_direction_set, tx, border)
    e_min = find_e_min(normalized_direction_set, tx, border)

    # Search the best scaling factor among the centroids
    midpoint_set = generate_midpoints(tx, e_max, e_min - delta)
    centroids = get_centroids(normalized_direction_set, midpoint_set, border)
    for centroid in centroids_accum + centroids:
        x_hat = chop_complex(centroid * x, tx)

        mu = np.vdot(x, x_hat) / (np.linalg.norm(x_hat, ord=2)**2)
        y_hat = chop_complex(mu * y, ty)

        new_c = c(x, y, x_hat, y_hat)
        if new_c < old_c:
            x_approx, y_approx = x_hat, y_hat
            lbd_approx, mu_approx = centroid, mu

            old_c = new_c

    return x_approx, y_approx, lbd_approx, mu_approx


def find_xy_complex(x, y, tx, delta, ty=None):
    """
    Returns a quantization for a rank-one matrix according to parameter delta.

    Set delta=0 to only have the centroids on the accumulation lines.

    Parameters
    ----------
    x: vector of size $m$ to quantize.
        numpy.ndarray
    y: vector of size $n$ to quantize.
        numpy.ndarray
    tx: Number of significand bits for $x$.
        int
    delta: Parameter that controls the number of breaklines in the algorithm.
        int
    ty: Number of significand bits for $y$, if None, then it will be tx.
        int

    Returns
    -------
    Quantized version of $x$ and $y$ and their scaling parameters.
        tuple(numpy.ndarray, numpy.ndarray, complex, complex)
    """
    if ty is None:
        ty = tx

    if x.shape <= y.shape:
        normalized_direction_set = normalize_direction_set(
            generate_directions(x))
        border = build_tiling_domain(normalized_direction_set, tx)

        x_approx, y_approx, lbd_approx, mu_approx = _find_xy_complex(
            x, normalized_direction_set, y, tx, ty, border, delta)
    else:
        normalized_direction_set = normalize_direction_set(
            generate_directions(y))
        border = build_tiling_domain(normalized_direction_set, ty)

        y_approx, x_approx, mu_approx, lbd_approx = _find_xy_complex(
            y, normalized_direction_set, x, ty, tx, border, delta)

    return x_approx, y_approx, lbd_approx, mu_approx


def find_xy_rtn_complex(x, y, t):
    """
    Returns a quantization for a rank-one matrix by using the Round-to-Nearest quantization approach.

    Parameters
    ----------
    x: vector of size $m$ to quantize.
        numpy.ndarray
    y: vector of size $n$ to quantize.
        numpy.ndarray
    tx: Number of significand bits for $x$.
        int

    Returns
    -------
    Quantized version of $x$ and $y$.
        tuple(numpy.ndarray, numpy.ndarray)
    """
    return chop_complex(x, t), chop_complex(y, t)


def find_xy_stochastic_complex(x, y, t):
    """
    Returns a quantization for a rank-one matrix by using the stochastic quantization approach.

    Parameters
    ----------
    x: vector of size $m$ to quantize.
        numpy.ndarray
    y: vector of size $n$ to quantize.
        numpy.ndarray
    tx: Number of significand bits for $x$.
        int

    Returns
    -------
    Quantized version of $x$ and $y$.
        tuple(numpy.ndarray, numpy.ndarray)
    """
    return stochastic_chop_complex(x, t), stochastic_chop_complex(y, t)


def find_xy_fixed_complex(x, y, t):
    """
    Returns a quantization for a rank-one matrix by using the fixed-point quantization approach.

    Parameters
    ----------
    x: vector of size $m$ to quantize.
        numpy.ndarray
    y: vector of size $n$ to quantize.
        numpy.ndarray
    tx: Number of significand bits for $x$.
        int

    Returns
    -------
    Quantized version of $x$ and $y$.
        tuple(numpy.ndarray, numpy.ndarray)
    """
    return fixed_chop_complex(x, t), fixed_chop_complex(y, t)
