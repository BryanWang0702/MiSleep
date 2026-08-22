# -*- coding: UTF-8 -*-
"""Light post-processing of predicted state sequences.

Applies only physiologically justified smoothing: Init -> Wake, Wake -> REM
transitions are forbidden (REM must follow NREM), and isolated single-epoch
flips are smoothed. Probabilities are left intact.
"""

from __future__ import annotations

import numpy as np


def smooth_constraints(pred_label, pred_prob=None):
    """Smooth a 1-indexed state sequence (1=NREM, 2=REM, 3=Wake, 4=Init).

    Rules (order matters):
      1. State 4 (Init) -> Wake (3).
      2. REM (2) immediately after Wake (3) -> NREM (1).
      3. A single epoch sandwiched between two equal states -> that state
         (unless it is Wake, left alone to avoid erasing brief arousals).

    Returns the smoothed 1-indexed list.
    """
    lab = [int(x) for x in pred_label]
    n = len(lab)
    if n == 0:
        return lab
    lab = [3 if x == 4 else x for x in lab]
    if n < 3:
        return lab

    # pass 1: REM after Wake -> NREM
    for i in range(1, n):
        if lab[i - 1] == 3 and lab[i] == 2:
            lab[i] = 1

    # pass 2: single-epoch flips (not Wake)
    out = list(lab)
    for i in range(1, n - 1):
        if out[i - 1] == out[i + 1] and out[i] != 3 and out[i] != out[i - 1]:
            out[i] = out[i - 1]

    return out


def expand_to_seconds(labels, epoch_s=5):
    """Expand per-epoch labels to per-second labels."""
    out = []
    for each in labels:
        out.extend([each] * epoch_s)
    return out
