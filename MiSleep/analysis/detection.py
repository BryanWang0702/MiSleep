from misleep.utils.signals import signal_filter
from scipy.signal import find_peaks
import numpy as np
import pandas as pd

def SWA_detection(signal, sf, freq_band=[0.5, 4], amp_threshold=(75, ), df=False, start_time_sec=0):
    """Slow wave activity detection
    Detect form trough to peaks with relative amplitude

    Parameters
    ----------
    signal : ndarray
        Signal to detect Slow wave activity
    sf : int or float
        Sampling frequency of signal
    freq_band : List
        Frequency band of slow wave activity
    amp_threshold : float
        minimum and maximum absolute amplitude
    df : bool, optional
        Whether return as a dataframe, when analyze with code, this will be useful
    start_time : float, optional
        When use gui, this will be useful to locate each state's analysis

    TODO: add relative methods
    """

    # filter
    band_data, _ = signal_filter(signal, sf, btype='bandpass', low=freq_band[0], high=freq_band[1])

    # Find peaks and zerocrossing
    pos_peak_idx, _ = find_peaks(band_data, amp_threshold)
    neg_peak_idx, _ = find_peaks(-1*band_data, amp_threshold)
    zero_crossing = np.where(np.diff(np.signbit(band_data), axis=0))[0]

    # Find zero -> neg_peak -> zero -> pos_peak -> zero
    negative_peaks_hold = []
    positive_peaks_hold = []
    zero_crossing_hold = []
    for neg_idx in neg_peak_idx:
        # find the zero cross after the current negative peak
        for zero_idx in zero_crossing:
            if zero_idx > neg_idx:
                # find the positive peak after the zero cross
                for pos_idx in pos_peak_idx:
                    if pos_idx > zero_idx and zero_idx not in zero_crossing_hold:
                        # no zero cross between pos and zero, neg and zero
                        if True not in (band_data[zero_idx+1: pos_idx] <= 0) and True not in (band_data[neg_idx: zero_idx] >= 0):
                            negative_peaks_hold.append(neg_idx)
                            positive_peaks_hold.append(pos_idx)
                            zero_crossing_hold.append(zero_idx)
                    
                        break
                break

    if negative_peaks_hold == []:
        return None
    # find the zero before negative peak and after positive peak
    # see np.searchsorted(a, v) insert v's element into a, find the index which will make the a's order preserve
    start_zero_cross_hold = zero_crossing[:-1][np.diff(np.searchsorted(negative_peaks_hold, zero_crossing)).astype(bool)]
    # start_zero_cross_hold = [start_zero_cross_hold, band_data[start_zero_cross_hold]]

    if zero_crossing[-1] < positive_peaks_hold[-1]:
        zero_crossing[-1] = np.append(zero_crossing, positive_peaks_hold[-1] + 1)
    end_zero_cross_hold = zero_crossing[np.searchsorted(zero_crossing, positive_peaks_hold)]
    # end_zero_cross_hold = [end_zero_cross_hold, band_data[end_zero_cross_hold]]

    df_lst = []
    for idx, start_zero in enumerate(start_zero_cross_hold):
        start_time = start_zero/sf + start_time_sec
        end_time = end_zero_cross_hold[idx]/sf + start_time_sec
        total_duration = end_time - start_time
        frequency = 1/total_duration
        if frequency > freq_band[1] or frequency < freq_band[0]:
            continue

        middle_cross_time = zero_crossing_hold[idx] / sf + start_time_sec

        time_pos_peak = positive_peaks_hold[idx] / sf + start_time_sec
        val_pos_peak = positive_peaks_hold[idx]
        time_neg_peak = negative_peaks_hold[idx] / sf + start_time_sec
        val_neg_peak = negative_peaks_hold[idx]

        peak_to_peak = val_pos_peak - val_neg_peak

        slope = peak_to_peak / (time_pos_peak - time_neg_peak)

        df_lst.append([start_time, time_neg_peak, middle_cross_time, time_pos_peak, 
                    end_time, total_duration, val_neg_peak, val_pos_peak, 
                    peak_to_peak, slope, frequency])

    if df:
        return pd.DataFrame(df_lst, columns=['StartTime', 'NegTime', 'MiddleTime', 
                                            'PosTime', 'EndTime', 'Duration', 'NegPeak', 
                                            'PosPeak', 'PTP', 'Slope', 'Frequency'])
    else:
        return df_lst
    

def spindle_detection(signal, freq_band=[10, 15]):
    """Spindle detection"""


def artifact_detection(signal):
    """Artifact detection"""



