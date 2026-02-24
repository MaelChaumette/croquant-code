import numpy as np
from scipy.sparse import csr_matrix


from lazylinop.butterfly import ksm


def soft_thresholding(x, threshold):
    """
    Applies soft-thresholding to a complex vector x with a given threshold.

    Parameters
    ----------
    x: Matrix to apply soft-thresholding
        numpy.ndarray
    threshold: Given threshold
        float

    Returns
    -------
    Matrix with soft-thresholding
        numpy.ndarray
    """
    y = np.zeros_like(x)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            u, v = np.real(x[i, j]), np.imag(x[i, j])
            if np.abs(u) > threshold:
                y[i, j] = u
            if np.abs(v) > threshold:
                y[i, j] += 1j * v

    return y


def apply_soft_thresholding(lazy_butterflies, threshold):
    """
    Applies soft-thresholding to a list of butterfly matrices.

    Parameters
    ----------
    butterflies: Butterfly factors to apply soft-thresholding.
        list[scipy.sparse.csr_matrix]
    threshold: Given threshold
        float

    Returns
    -------
    Butterfly factors with soft-thresholding
        list[scipy.sparse.csr_matrix]
    """
    new_butterflies = []
    for butterfly in lazy_butterflies.ks_values:
        butterfly = ksm(butterfly).toarray()

        new_butterflies.append(csr_matrix(
            soft_thresholding(butterfly, threshold)))

    return new_butterflies


def get_fft_butterflies(N):
    """
    Creates the FFT butterfly factorization matrices for size N.
    """
    if not (N > 0 and (N & (N - 1)) == 0):
        raise ValueError("N must be a power of 2")

    n_stages = int(np.log2(N))
    matrices = []

    for s in range(1, n_stages + 1):
        # Butterfly block size at this stage
        block_size = 2**s
        half_block = 2**(s-1)

        # Initialization of the matrix at stage s
        mat_s = np.zeros((N, N), dtype=complex)

        # Twiddle factors for this stage
        # exp(-2j * pi * k / block_size)
        twiddles = np.exp(-2j * np.pi * np.arange(half_block) / block_size)

        # Filling by blocks
        for i in range(0, N, block_size):
            for k in range(half_block):
                # Standard butterfly structure
                # Upper index: i + k
                # Lower index: i + k + half_block

                # Upper output = Upper input + W * Lower input
                mat_s[i + k, i + k] = 1
                mat_s[i + k, i + k + half_block] = twiddles[k]

                # Lower output = Upper input - W * Lower input
                mat_s[i + k + half_block, i + k] = 1
                mat_s[i + k + half_block, i + k + half_block] = -twiddles[k]

        matrices.append(csr_matrix(mat_s))

    return matrices


def cost_fft(butterflies, butterflies_hat):
    """
    Returns the error made by a quantization algorithm that generates butterflies_hat from butterflies.

    Parameters
    ----------
    butterflies: Original butterfly factors.
        list[scipy.sparse.csr_matrix]
    butterflies_hat: Quantized butterfly factors.
        list[scipy.sparse.csr_matrix]

    Returns
    -------
    Quantized error
        float
    """
    x = np.random.randn(butterflies[0].shape[0])

    signal = butterflies[0]
    signal_hat = butterflies_hat[0]
    for butterfly, butterfly_hat in zip(butterflies[1:], butterflies_hat[1:]):
        signal = signal @ butterfly
        signal_hat = signal_hat @ butterfly_hat

    signal = signal @ x
    signal_hat = signal_hat @ x

    return np.linalg.norm(signal - signal_hat) / np.linalg.norm(signal)
