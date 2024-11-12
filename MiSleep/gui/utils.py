from misleep.io.base import MiAnnotation
import pandas as pd

import datetime

def create_new_mianno(data_duration):
    """Create a new MiAnnotation object"""
    marker = []
    start_end = []
    sleep_state = [4 for _ in range(data_duration)]
    return MiAnnotation(sleep_state=sleep_state, start_end=start_end, marker=marker)


def second2time(second, ac_time, ms=False):
    """
    Pass second, return time format %d:%H:%M:%S from acquisition time
    :param second:
    :param ac_time: acquisition time
    :return:
    """

    if ms:
        return (ac_time + datetime.timedelta(seconds=second)).strftime(
            f"%d:%H:%M:%S:{str(second).split('.')[1]}")
    return (ac_time + datetime.timedelta(seconds=second)).strftime("%d:%H:%M:%S")


def transfer_time(date_time, seconds, date_time_format='%d:%H:%M:%S', ms=False):
    """
    Add seconds to the date time and transfer to the target format

    Parameters
    ----------
    date_time : datetime object
        The date time we want to start with, here is the reset acquisition time
    seconds : int
        Seconds going to add to the date_time
    date_time_format : str
        Final format of date_time. Defaults is '%d:%M:%H:%S'
    ms : bool
        Whether keep ms

    Returns
    -------
    target_time : str
        Final date time in string format

    Examples
    --------
    Add seconds to the datetime

    >>> import datetime
    >>> original_time = datetime.datetime(2024, 1, 30, 10, 50, 0)
    >>> seconds = 40
    >>> format_ = '%d-%M:%H:%S'
    >>> transfer_time(original_time, seconds, format_)
    '30-10:50:40'
    """

    temp_time = date_time + datetime.timedelta(seconds=seconds)
    if ms:
        return f"{temp_time.strftime(format=date_time_format)}.{str(seconds).split('.')[1]}"
    return temp_time.strftime(format=date_time_format)


def insert_row(df, idx, row):
    """
    Insert a row to a dataframe in a specific position

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe for operation
    idx : int
        index to insert the row, insert below the row
    row : series
        Row to insert

    Returns
    -------
    result_df : pandas.DataFrame
    """
    if isinstance(row, pd.Series):
        row = pd.DataFrame(row).T
    df = pd.concat([df[:idx], row, df[idx:]], axis=0).reset_index(drop=True)
    return df


def temp_loop4below_row(row, acquisition_time, columns):
    """
    Just for below row repetition
    Returns
    -------

    """

    seconds_ = (int(row['start_time_sec'] / 3600) + 1) * 3600
    previous_row = pd.Series([
        row['start_time'], row['start_time_sec'], '1',
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, '0', row['state_code'], row['state']
    ], index=columns)

    new_row = pd.Series([
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, ' ',
        transfer_time(acquisition_time, seconds_, '%Y-%m-%d %H:%M:%S'),
        seconds_, ' ', '5', 'MARKER'
    ], index=columns)

    below_row = pd.Series([
        transfer_time(acquisition_time, seconds_ + 1, '%Y-%m-%d %H:%M:%S'),
        seconds_ + 1, '1', row['end_time'], row['end_time_sec'],
        '0', row['state_code'], row['state']
    ], index=columns)

    return previous_row, new_row, below_row

def cal_draw_spectrum(data, sf, nperseg, freq_band=None, relative=None):
    """
    Calculate the relative power spectrum of data, and plot

    Parameters
    ----------
    data : 1-D array
        data for calculation
    sf : int
        sampling frequency of data
    nperseg : int
        for welch fourier transform
    freq_band : list
        frequency band low and high frequency
    relative : bool

    Returns
    -------
    spectrum : 2-D array
        spectrum frequency and power
    figure : matplotlib.figure()
        spectrum figure
    """
    from scipy.signal import welch
    import numpy as np
    import matplotlib.pyplot as plt

    if freq_band is None:
        freq_band = [0.5, 30]
    F, P = welch(data, sf, nperseg=nperseg)
    
    F = np.array([round(each, 1) for each in F])

    # find frequency band
    if freq_band is not None:
        idx_band = np.logical_and(F >= freq_band[0], F <= freq_band[1])
        F = F[idx_band]
        P = P[idx_band]

    # Get relative power
    if relative:
        P = [each/sum(P) for each in P]

    major_ticks_top = np.linspace(0, 50, 26)
    minor_ticks_top = np.linspace(0, 50, 51)

    figure = plt.figure(figsize=(10, 7))
    ax = figure.subplots(nrows=1, ncols=1)
    plt.subplots_adjust(top=0.95, left=0.15, bottom=0.15, right=0.95)

    ax.xaxis.set_ticks(major_ticks_top)
    ax.xaxis.set_ticks(minor_ticks_top, minor=True)
    ax.grid(which="major", alpha=0.6)
    ax.grid(which="minor", alpha=0.3)

    ax.set_xlim(freq_band[0], freq_band[1])
    ax.plot(F, P)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power spectral density (Power/Hz)")

    return np.array([F, P]), figure


def identify_startend_color(dict_, state_name, end=False):
    """return the color of state while state name is in the dict or return blue"""
    if state_name in dict_.keys():
        return dict_[state_name]
    else:
        return "blue"
