# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: signals.py
@Author: Xueqiang Wang
@Date: 2025/2/21
@Description:  Self implemente some functions from the 'antropy' package, 
because to import the antropy package cost a lot of time
I just copy the functions there
"""

import numpy as np
from math import factorial

def num_zerocross(x, normalize=False, axis=-1):
    """Number of zero-crossings.

    .. versionadded: 0.1.3

    Parameters
    ----------
    x : list or np.array
        1D or N-D data.
    normalize : bool
        If True, divide by the number of samples to normalize the output
        between 0 and 1. Otherwise, return the absolute number of zero
        crossings.
    axis : int
        The axis along which to perform the computation. Default is -1 (last).

    Returns
    -------
    nzc : int or float
        Number of zero-crossings.

    Examples
    --------
    Simple examples

    >>> import numpy as np
    >>> import antropy as ant
    >>> ant.num_zerocross([-1, 0, 1, 2, 3])
    1

    >>> ant.num_zerocross([0, 0, 2, -1, 0, 1, 0, 2])
    2

    Number of zero crossings of a pure sine

    >>> import numpy as np
    >>> import antropy as ant
    >>> sf, f, dur = 100, 1, 4
    >>> N = sf * dur # Total number of discrete samples
    >>> t = np.arange(N) / sf # Time vector
    >>> x = np.sin(2 * np.pi * f * t)
    >>> ant.num_zerocross(x)
    7

    Random 2D data

    >>> np.random.seed(42)
    >>> x = np.random.normal(size=(4, 3000))
    >>> ant.num_zerocross(x)
    array([1499, 1528, 1547, 1457])

    Same but normalized by the number of samples

    >>> np.round(ant.num_zerocross(x, normalize=True), 4)
    array([0.4997, 0.5093, 0.5157, 0.4857])

    Fractional Gaussian noise with H = 0.5

    >>> import stochastic.processes.noise as sn
    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.5, rng=rng).sample(10000)
    >>> print(f"{ant.num_zerocross(x, normalize=True):.4f}")
    0.4973

    Fractional Gaussian noise with H = 0.9

    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.9, rng=rng).sample(10000)
    >>> print(f"{ant.num_zerocross(x, normalize=True):.4f}")
    0.2615

    Fractional Gaussian noise with H = 0.1

    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.1, rng=rng).sample(10000)
    >>> print(f"{ant.num_zerocross(x, normalize=True):.4f}")
    0.6451
    """
    x = np.asarray(x)
    # https://stackoverflow.com/a/29674950/10581531
    nzc = np.diff(np.signbit(x), axis=axis).sum(axis=axis)
    if normalize:
        nzc = nzc / x.shape[axis]
    return nzc


def hjorth_params(x, axis=-1):
    """Calculate Hjorth mobility and complexity on given axis.

    .. versionadded: 0.1.3

    Parameters
    ----------
    x : list or np.array
        1D or N-D data.
    axis : int
        The axis along which to perform the computation. Default is -1 (last).

    Returns
    -------
    mobility, complexity : float
        Mobility and complexity parameters.

    Notes
    -----
    Hjorth Parameters are indicators of statistical properties used in signal
    processing in the time domain introduced by Bo Hjorth in 1970. The
    parameters are activity, mobility, and complexity. EntroPy only returns the
    mobility and complexity parameters, since activity is simply the variance
    of :math:`x`, which can be computed easily with :py:func:`numpy.var`.

    The **mobility** parameter represents the mean frequency or the proportion
    of standard deviation of the power spectrum. This is defined as the square
    root of variance of the first derivative of :math:`x` divided by the
    variance of :math:`x`.

    The **complexity** gives an estimate of the bandwidth of the signal, which
    indicates the similarity of the shape of the signal to a pure sine wave
    (where the value converges to 1). Complexity is defined as the ratio of
    the mobility of the first derivative of :math:`x` to the mobility of
    :math:`x`.

    References
    ----------
    - https://en.wikipedia.org/wiki/Hjorth_parameters
    - https://doi.org/10.1016%2F0013-4694%2870%2990143-4

    Examples
    --------
    Hjorth parameters of a pure sine

    >>> import numpy as np
    >>> import antropy as ant
    >>> sf, f, dur = 100, 1, 4
    >>> N = sf * dur # Total number of discrete samples
    >>> t = np.arange(N) / sf # Time vector
    >>> x = np.sin(2 * np.pi * f * t)
    >>> np.round(ant.hjorth_params(x), 4)
    array([0.0627, 1.005 ])

    Random 2D data

    >>> np.random.seed(42)
    >>> x = np.random.normal(size=(4, 3000))
    >>> mob, com = ant.hjorth_params(x)
    >>> print(mob)
    [1.42145064 1.4339572  1.42186993 1.40587512]

    >>> print(com)
    [1.21877527 1.21092261 1.217278   1.22623163]

    Fractional Gaussian noise with H = 0.5

    >>> import stochastic.processes.noise as sn
    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.5, rng=rng).sample(10000)
    >>> np.round(ant.hjorth_params(x), 4)
    array([1.4073, 1.2283])

    Fractional Gaussian noise with H = 0.9

    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.9, rng=rng).sample(10000)
    >>> np.round(ant.hjorth_params(x), 4)
    array([0.8395, 1.9143])

    Fractional Gaussian noise with H = 0.1

    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.1, rng=rng).sample(10000)
    >>> np.round(ant.hjorth_params(x), 4)
    array([1.6917, 1.0717])
    """
    x = np.asarray(x)
    # Calculate derivatives
    dx = np.diff(x, axis=axis)
    ddx = np.diff(dx, axis=axis)
    # Calculate variance
    x_var = np.var(x, axis=axis)  # = activity
    dx_var = np.var(dx, axis=axis)
    ddx_var = np.var(ddx, axis=axis)
    # Mobility and complexity
    mob = np.sqrt(dx_var / x_var)
    com = np.sqrt(ddx_var / dx_var) / mob
    return mob, com


def perm_entropy(x, order=3, delay=1, normalize=False):
    """Permutation Entropy.

    Parameters
    ----------
    x : list or np.array
        One-dimensional time series of shape (n_times)
    order : int
        Order of permutation entropy. Default is 3.
    delay : int, list, np.ndarray or range
        Time delay (lag). Default is 1. If multiple values are passed
        (e.g. [1, 2, 3]), AntroPy will calculate the average permutation
        entropy across all these delays.
    normalize : bool
        If True, divide by log2(order!) to normalize the entropy between 0
        and 1. Otherwise, return the permutation entropy in bit.

    Returns
    -------
    pe : float
        Permutation Entropy.

    Notes
    -----
    The permutation entropy is a complexity measure for time-series first
    introduced by Bandt and Pompe in 2002.

    The permutation entropy of a signal :math:`x` is defined as:

    .. math:: H = -\\sum p(\\pi)\\log_2(\\pi)

    where the sum runs over all :math:`n!` permutations :math:`\\pi` of order
    :math:`n`. This is the information contained in comparing :math:`n`
    consecutive values of the time series. It is clear that
    :math:`0 ≤ H (n) ≤ \\log_2(n!)` where the lower bound is attained for an
    increasing or decreasing sequence of values, and the upper bound for a
    completely random system where all :math:`n!` possible permutations appear
    with the same probability.

    The embedded matrix :math:`Y` is created by:

    .. math::
        y(i)=[x_i,x_{i+\\text{delay}}, ...,x_{i+(\\text{order}-1) *
        \\text{delay}}]

    .. math:: Y=[y(1),y(2),...,y(N-(\\text{order}-1))*\\text{delay})]^T

    References
    ----------
    Bandt, Christoph, and Bernd Pompe. "Permutation entropy: a
    natural complexity measure for time series." Physical review letters
    88.17 (2002): 174102.

    Examples
    --------
    Permutation entropy with order 2

    >>> import numpy as np
    >>> import antropy as ant
    >>> import stochastic.processes.noise as sn
    >>> x = [4, 7, 9, 10, 6, 11, 3]
    >>> # Return a value in bit between 0 and log2(factorial(order))
    >>> print(f"{ant.perm_entropy(x, order=2):.4f}")
    0.9183

    Normalized permutation entropy with order 3

    >>> # Return a value comprised between 0 and 1.
    >>> print(f"{ant.perm_entropy(x, normalize=True):.4f}")
    0.5888

    Fractional Gaussian noise with H = 0.5, averaged across multiple delays
    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.5, rng=rng).sample(10000)
    >>> print(f"{ant.perm_entropy(x, delay=[1, 2, 3], normalize=True):.4f}")
    0.9999

    Fractional Gaussian noise with H = 0.1, averaged across multiple delays

    >>> rng = np.random.default_rng(seed=42)
    >>> x = sn.FractionalGaussianNoise(hurst=0.1, rng=rng).sample(10000)
    >>> print(f"{ant.perm_entropy(x, delay=[1, 2, 3], normalize=True):.4f}")
    0.9986

    Random

    >>> rng = np.random.default_rng(seed=42)
    >>> print(f"{ant.perm_entropy(rng.random(1000), normalize=True):.4f}")
    0.9997

    Pure sine wave

    >>> x = np.sin(2 * np.pi * 1 * np.arange(3000) / 100)
    >>> print(f"{ant.perm_entropy(x, normalize=True):.4f}")
    0.4463

    Linearly-increasing time-series

    >>> x = np.arange(1000)
    >>> print(f"{ant.perm_entropy(x, normalize=True):.4f}")
    -0.0000
    """
    # If multiple delay are passed, return the average across all d
    if isinstance(delay, (list, np.ndarray, range)):
        return np.mean([perm_entropy(x, order=order, delay=d, normalize=normalize) for d in delay])
    x = np.array(x)
    ran_order = range(order)
    hashmult = np.power(order, ran_order)
    assert delay > 0, "delay must be greater than zero."
    # Embed x and sort the order of permutations
    sorted_idx = _embed(x, order=order, delay=delay).argsort(kind="quicksort")
    # Associate unique integer to each permutations
    hashval = (np.multiply(sorted_idx, hashmult)).sum(1)
    # Return the counts
    _, c = np.unique(hashval, return_counts=True)
    # Use np.true_divide for Python 2 compatibility
    p = np.true_divide(c, c.sum())
    pe = -_xlogx(p).sum()
    if normalize:
        pe /= np.log2(factorial(order))
    return pe

def _embed(x, order=3, delay=1):
    """Time-delay embedding.

    Parameters
    ----------
    x : array_like
        1D-array of shape (n_times) or 2D-array of shape (signal_indice, n_times)
    order : int
        Embedding dimension (order).
    delay : int
        Delay.

    Returns
    -------
    embedded : array_like
        Embedded time series, of shape (..., n_times - (order - 1) * delay, order)
    """
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
        # 1D array (n_times)
        Y = np.zeros((order, N - (order - 1) * delay))
        for i in range(order):
            Y[i] = x[(i * delay) : (i * delay + Y.shape[1])]
        return Y.T
    else:
        # 2D array (signal_indice, n_times)
        Y = []
        # pre-defiend an empty list to store numpy.array (concatenate with a list is faster)
        embed_signal_length = N - (order - 1) * delay
        # define the new signal length
        indice = [[(i * delay), (i * delay + embed_signal_length)] for i in range(order)]
        # generate a list of slice indice on input signal
        for i in range(order):
            # loop with the order
            temp = x[:, indice[i][0] : indice[i][1]].reshape(-1, embed_signal_length, 1)
            # slicing the signal with the indice of each order (vectorized operation)
            Y.append(temp)
            # append the sliced signal to list
        Y = np.concatenate(Y, axis=-1)
        return Y


def _xlogx(x, base=2):
    """Returns x log_b x if x is positive, 0 if x == 0, and np.nan
    otherwise. This handles the case when the power spectrum density
    takes any zero value.
    """
    x = np.asarray(x)
    xlogx = np.zeros(x.shape)
    xlogx[x < 0] = np.nan
    valid = x > 0
    xlogx[valid] = x[valid] * np.log(x[valid]) / np.log(base)
    return xlogx

