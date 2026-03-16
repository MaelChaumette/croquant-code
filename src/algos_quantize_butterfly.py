import numpy as np

from scipy.sparse import csr_matrix

from src.complex_case import chop_complex, stochastic_chop_complex, fixed_chop_complex
from src.algos_quantize_rank_one import find_xy_complex, find_xy_complex


def find_optim_product_complex(X, Y, tx, ty, delta=2):
    """
    Finds the optimal quantization for a product of two matrices, $X$ and $Y$,
    when the rank-one matrices $x_i y_i^\top$, where $x_i$ and $y_i$ are the corresponding columns of $X$ and $Y$,
    have disjoints supports.

    Parameters
    ----------
    X: Left matrix of size $m \times r$ to quantize.
        numpy.ndarray
    Y: Right matrix of size $n \times r$ to quantize.
        numpy.ndarray
    tx: Number of significand bits for $X$.
        int
    ty: Number of significand bits for $Y$.
        int
    delta: Parameter that controls the number of breaklines in the algorithm.
        int

    Returns
    -------
    Quantized version of $X$ and $Y$.
        tuple(numpy.ndarray, numpy.ndarray)
    """
    Lbd = np.zeros(X.shape[0], dtype=complex)
    Mu = np.zeros(X.shape[0], dtype=complex)

    for i in range(X.shape[0]):
        xi, yi = X[:, i], Y[:, i]
        _, _, lbd, mu = find_xy_complex(
            xi[xi.nonzero()], yi[yi.nonzero()], tx, delta, ty)
        Lbd[i], Mu[i] = lbd, mu

    return chop_complex(X * Lbd, tx), chop_complex(Y * Mu, ty), Lbd, Mu


def butterfly_quantize_pairwise(butterflies, t, delta=2):
    """
    Quantizes a product of butterfly matrices by using the pairwise heuristic.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int
    delta: Parameter that controls the number of breaklines in the algorithm.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    quantized_butterflies = []

    L = len(butterflies)
    for l in range(int(L / 2)):

        B_odd = butterflies[2 * l]
        B_even = butterflies[2 * l + 1]

        B_odd_hat, B_even_hat, _, _ = find_optim_product_complex(
            B_odd.toarray(), B_even.getH().toarray(), t, t, delta)

        quantized_butterflies.extend(
            [csr_matrix(B_odd_hat), csr_matrix(B_even_hat).getH()])

    if L % 2 != 0:
        B_last = butterflies[L - 1]

        quantized_butterflies.append(
            csr_matrix(chop_complex(B_last.toarray(), t)))

    return quantized_butterflies


def butterfly_quantize_ltr(butterflies, t, delta=2):
    """
    Quantizes a product of butterfly matrices by using the Left-to-Right heuristic.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int
    delta: Parameter that controls the number of breaklines in the algorithm.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    quantized_butterflies = []

    L = len(butterflies)

    def product(matrices, index):
        result = matrices[index]
        for i in range(1, L - index):
            result = result @ matrices[i + index]

        return result

    X = butterflies[0].toarray()
    Y = product(butterflies, 1).toarray()

    for l in range(1, L - 1):
        X_hat, _, _, Mu = find_optim_product_complex(
            X, Y.conj().T, t, np.inf, delta)

        quantized_butterflies.append(csr_matrix(X_hat))

        X = Mu[:, np.newaxis].conj() * butterflies[l].toarray()
        Y = product(butterflies, l + 1).toarray()

    X_hat, Y_hat, _, _ = find_optim_product_complex(X, Y.conj().T, t, t, delta)
    quantized_butterflies.extend([csr_matrix(X_hat), csr_matrix(Y_hat).getH()])

    return quantized_butterflies


def butterfly_quantize_rtl(butterflies, t, delta=2):
    """
    Quantizes a product of butterfly matrices by using the Right-to-Left heuristic.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int
    delta: Parameter that controls the number of breaklines in the algorithm.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    quantized_butterflies = []

    def product(matrices):
        result = matrices[0].copy()
        for matrix in matrices[1:]:
            result = result @ matrix

        return result

    X = product(butterflies[:-1]).toarray()
    Y = butterflies[-1].toarray()

    for l in range(1, len(butterflies) - 1):
        _, Y_hat, Lbd, _ = find_optim_product_complex(
            X, Y.conj().T, np.inf, t, delta)

        quantized_butterflies.append(csr_matrix(Y_hat).getH())

        X = product(butterflies[:-(l + 1)]).toarray()
        Y = butterflies[-(l + 1)].toarray() * Lbd

    X_hat, Y_hat, _, _ = find_optim_product_complex(
        csr_matrix(X), csr_matrix(Y).getH(), t, t, delta)
    quantized_butterflies.extend([csr_matrix(Y_hat).getH(), csr_matrix(X_hat)])

    return reversed(quantized_butterflies)


def butterfly_quantize_rtn(butterflies, t):
    """
    Quantizes a product of butterfly matrices by using the Round-to-Nearest quantization approach.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    return [csr_matrix(chop_complex(butterflies[l].toarray(), t)) for l in range(len(butterflies))]


def butterfly_quantize_stochastic(butterflies, t):
    """
    Quantizes a product of butterfly matrices by using the stochastic quantization approach.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    return [csr_matrix(stochastic_chop_complex(butterflies[l].toarray(), t)) for l in range(len(butterflies))]


def butterfly_quantize_fixed(butterflies, t):
    """
    Quantizes a product of butterfly matrices by using the fixed point quantization approach.

    Parameters
    ----------
    butterflies: butterfly factors to quantize.
        list[scipy.sparse.csr_matrix]
    t: Number of significand bits.
        int

    Returns
    -------
    list of sparse butterfly factors
        list[scipy.sparse.csr_matrix]
    """
    return [csr_matrix(fixed_chop_complex(butterflies[l].toarray(), t)) for l in range(len(butterflies))]
