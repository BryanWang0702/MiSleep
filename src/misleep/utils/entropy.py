# -*- coding: UTF-8 -*-
"""Self-contained implementations of a few signal-complexity measures.

These functions were originally copied from the `antropy` package
(https://github.com/raphaelvallat/antropy, BSD-3-Clause) so that MiSleep
does not need to import the whole package just for three functions --
importing antropy used to cost a lot of startup time.
"""

import numpy as np
from math import factorial


def num_zerocross(x, normalize=False, axis=-1):
    """Number of zero-crossings of a signal.

    Parameters
    ----------
    x : array_like
        1-D or N-D data.
    normalize : bool
        If True, divide by the number of samples (output in ``[0, 1]``).
    axis : int
        Axis along which to compute. Default is -1.

    Returns
    -------
    nzc : int or ndarray
        Number of zero-crossings.
    """
    x = np.asarray(x)
    nzc = np.diff(np.signbit(x), axis=axis).sum(axis=axis)
    if normalize:
        nzc = nzc / x.shape[axis]
    return nzc


def hjorth_params(x, axis=-1):
    """Calculate Hjorth mobility and complexity on the given axis.

    Parameters
    ----------
    x : array_like
        1-D or N-D data.
    axis : int
        Axis along which to compute. Default is -1.

    Returns
    -------
    mobility, complexity : float or ndarray
        Hjorth mobility and complexity parameters.
    """
    x = np.asarray(x)
    dx = np.diff(x, axis=axis)
    ddx = np.diff(dx, axis=axis)
    x_var = np.var(x, axis=axis)  # = activity
    dx_var = np.var(dx, axis=axis)
    ddx_var = np.var(ddx, axis=axis)
    mob = np.sqrt(dx_var / x_var)
    com = np.sqrt(ddx_var / dx_var) / mob
    return mob, com


def perm_entropy(x, order=3, delay=1, normalize=False):
    """Permutation entropy (Bandt & Pompe, 2002).

    Parameters
    ----------
    x : array_like
        1-D time series.
    order : int
        Order of permutation entropy (embedding dimension). Default is 3.
    delay : int or array_like
        Time delay (lag). When several delays are given, the average
        permutation entropy across them is returned.
    normalize : bool
        If True, divide by ``log2(order!)`` so the output lies in [0, 1].

    Returns
    -------
    pe : float
        Permutation entropy (in bits, unless normalized).
    """
    if isinstance(delay, (list, np.ndarray, range)):
        return np.mean([perm_entropy(x, order=order, delay=d, normalize=normalize) for d in delay])
    x = np.array(x)
    ran_order = range(order)
    hashmult = np.power(order, ran_order)
    assert delay > 0, "delay must be greater than zero."
    sorted_idx = _embed(x, order=order, delay=delay).argsort(kind="quicksort")
    hashval = (np.multiply(sorted_idx, hashmult)).sum(1)
    _, c = np.unique(hashval, return_counts=True)
    p = np.true_divide(c, c.sum())
    pe = -_xlogx(p).sum()
    if normalize:
        pe /= np.log2(factorial(order))
    return pe


def _embed(x, order=3, delay=1):
    """Time-delay embedding of a 1-D or 2-D array."""
    x = np.asarray(x)
    N = x.shape[-1]
    assert x.ndim in [1, 2], "Only 1D or 2D arrays are currently supported."
    if order * delay > N:
        raise ValueError("Error: order * delay should be lower than x.size")
    if delay < 1:
        raise ValueError("Delay has to be at least 1.")
    if order < 2:
        raise ValueError("Order has to be at least 2.")

    if x.ndim == 1:
        Y = np.zeros((order, N - (order - 1) * delay))
        for i in range(order):
            Y[i] = x[(i * delay): (i * delay + Y.shape[1])]
        return Y.T
    else:
        Y = []
        embed_signal_length = N - (order - 1) * delay
        indice = [[(i * delay), (i * delay + embed_signal_length)] for i in range(order)]
        for i in range(order):
            temp = x[:, indice[i][0]: indice[i][1]].reshape(-1, embed_signal_length, 1)
            Y.append(temp)
        Y = np.concatenate(Y, axis=-1)
        return Y


def _xlogx(x, base=2):
    """Return ``x * log_b(x)`` for positive x, 0 for x == 0, else nan."""
    x = np.asarray(x)
    xlogx = np.zeros(x.shape)
    xlogx[x < 0] = np.nan
    valid = x > 0
    xlogx[valid] = x[valid] * np.log(x[valid]) / np.log(base)
    return xlogx
