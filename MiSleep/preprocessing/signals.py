# Preprocessing the signals, contains artifact rejection
# from yasa import art_detect

# def reject_artifact(signals, sf, methods=None, threshold=None):
#     """Currently use Raphael's algorithm --- yasa.art_detect

#     Parameters
#     ----------
#     signals : nd-array
#         data to do rejection
#     sf : int
#         sampling rate
#     methods : str, optional
#         yasa.art_detect method, {'covar', 'std'}. Defatul is 'std'
#     threshold : int, optional
#         yasa.art_detect threshold, channels to consideration
#     """
#     import numpy as np
#     if methods == None:
#         methods = 'std'
#     if threshold == None:
#         threshold = 1
    

#     art, _ = art_detect(signals, sf, window=5, method=methods, threshold=threshold)
#     art = np.repeat(art, int(5*sf))

#     # Reject data
#     signals = [each[art] for each in signals[:art.shape[0]]]

    # return signals

import numpy as np

def z_score(signal):
    """Z socre list, the formula is x-mean / std"""
    lst_mean = np.mean(signal, axis=0)
    lst_std = np.std(signal, axis=0)
    normalized_data = (signal - lst_mean) / lst_std
    return normalized_data

def reject_artifact(signal, sf=None, threshold=2):
    """
    reject artfact with signal channel standard deviation
    """
    
    signal = z_score(signal)
    # get epoch data
    signal = [signal[int(each): int((each+5*sf))] for each in range(0, signal.shape[0], int(5*sf))]
    signal_SD_lst = [np.std(each) for each in signal]
    ave_siganal_sd = np.mean(signal_SD_lst)
    artifacts_idx = []

    for each in signal_SD_lst:
        if each / ave_siganal_sd >= threshold:
            artifacts_idx.append(0)
        else:
            artifacts_idx.append(1)
    
    artifacts_idx = np.array(artifacts_idx).astype(bool)
    artifacts_idx = np.repeat(artifacts_idx, int(5*sf))
    signal = [item for each in signal for item in each]
    slice_length = artifacts_idx.shape[0] if artifacts_idx.shape[0] < len(signal) else len(signal)
    signal = np.array(signal[:slice_length])[artifacts_idx[:slice_length]]
    
    return signal



