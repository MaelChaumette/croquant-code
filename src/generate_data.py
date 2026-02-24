import numpy as np


def soft_thresholding(x, threshold):
    y = np.zeros_like(x)
    for i in range(x.shape[0]):
        a, b = np.real(x[i]), np.imag(x[i])
        if np.abs(a) > threshold:
            y[i] = a
        if np.abs(b) > threshold:
            y[i] += 1j * b

    return y


def random_unit_roots(n, m=32):
    k = np.random.randint(0, m, size=n)

    return soft_thresholding(np.exp(2j * np.pi * k / m), 1e-6)


def unit_roots(n):
    return soft_thresholding(np.exp(2j * np.pi * np.arange(n) / n), 1e-6)


def generate_alphabet(m=32):
    alphabet = []
    for k in range(m):
        z = np.random.rand() + 1j * np.random.rand()
        alphabet.append(z)

    return np.array(alphabet)


def random_finite_alphabet(n, alphabet):
    k = np.random.randint(0, len(alphabet), size=n)

    return alphabet[k]
