# -*- coding: UTF-8 -*-
"""Hidden-Markov-Model post-processing of the classifier output.

A 3-state HMM (NREM / REM / Wake) is learned from the *true* training
labels and stored with each benchmark model; the most probable state
sequence is decoded with Viterbi given the classifier probabilities
(emissions) and the learned transition structure.
"""

from __future__ import annotations

import numpy as np

STATES = (1, 2, 3)  # NREM, REM, Wake
N_STATES = 3


def learn_transitions(labels, smoothing=1e-3):
    """Learn HMM parameters (pi, A) from a state sequence.

    ``labels``: array of state codes (1/2/3). Returns ``pi`` (initial
    probabilities) and ``A`` (NxN transition matrix).
    """
    labels = np.asarray(labels, dtype=int)
    pi = np.zeros(N_STATES)
    A = np.zeros((N_STATES, N_STATES))
    idx = {s: i for i, s in enumerate(STATES)}
    valid = labels[labels != 4]
    if valid.size == 0:
        return (np.full(N_STATES, 1 / N_STATES),
                np.full((N_STATES, N_STATES), 1 / N_STATES))
    pi[idx[valid[0]]] += 1
    for i in range(valid.size - 1):
        A[idx[valid[i]], idx[valid[i + 1]]] += 1
    pi = (pi + smoothing) / (pi + smoothing).sum()
    A = (A + smoothing)
    A = A / A.sum(axis=1, keepdims=True)
    return pi, A


def probs_to_emission(probs, priors):
    """Convert P(state|x) to observation likelihood P(x|state) via Bayes.

    ``probs``: (T, N) classifier probabilities in state order (1,2,3).
    ``priors``: (N,) marginal state probabilities.
    """
    probs = np.asarray(probs, dtype=np.float64)
    priors = np.asarray(priors, dtype=np.float64)
    priors = np.maximum(priors, 1e-6)
    emission = probs / priors[None, :]
    emission = emission / emission.sum(axis=1, keepdims=True)
    return emission


def viterbi(emission_log, pi, logA):
    """Viterbi decoding. ``emission_log``: (T, N) log-likelihoods.

    Returns the most likely state sequence (codes 1/2/3).
    """
    T, N = emission_log.shape
    logpi = np.log(np.maximum(pi, 1e-12))
    delta = np.empty((T, N))
    psi = np.zeros((T, N), dtype=int)
    delta[0] = logpi + emission_log[0]
    for t in range(1, T):
        prev = delta[t - 1][:, None] + logA
        psi[t] = np.argmax(prev, axis=0)
        delta[t] = emission_log[t] + prev[psi[t], np.arange(N)]
    path = np.zeros(T, dtype=int)
    path[-1] = np.argmax(delta[-1])
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]
    return np.asarray(STATES)[path]


def _logsumexp(x, axis=None, keepdims=False):
    x = np.asarray(x, dtype=np.float64)
    m = x.max(axis=axis, keepdims=True)
    out = np.log(np.exp(x - m).sum(axis=axis, keepdims=True)) + m
    return out if keepdims else np.squeeze(out, axis=axis)


def forward_backward(emission_log, pi, logA):
    """Log-space forward-backward; returns per-epoch state posteriors.

    ``emission_log``: (T, N) log-likelihoods, ``pi`` initial probabilities,
    ``logA`` (N, N) log transition matrix. Returns a (T, N) array whose
    entry ``[t, s]`` is P(state_t = s | all observations) - the true
    HMM-informed confidence of each state at each epoch.
    """
    T, N = emission_log.shape
    logpi = np.log(np.maximum(pi, 1e-12))
    logA = np.asarray(logA, dtype=np.float64)

    # forward pass
    alpha = np.empty((T, N))
    alpha[0] = logpi + emission_log[0]
    for t in range(1, T):
        alpha[t] = emission_log[t] + _logsumexp(
            alpha[t - 1][:, None] + logA, axis=0)

    # backward pass
    beta = np.zeros((T, N))
    for t in range(T - 2, -1, -1):
        beta[t] = _logsumexp(
            logA + beta[t + 1][None, :] + emission_log[t + 1][None, :], axis=1)

    loggamma = alpha + beta
    loggamma = loggamma - _logsumexp(loggamma, axis=1, keepdims=True)
    return np.exp(loggamma)
