# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/21
@Description:   Load data from .mat or .edf file, write data into .mat file
                Data contains: Signals, channel name, sampling frequency

                20240228: Use MiData format for the final output
"""

from hdf5storage import loadmat, savemat
import pyedflib
import datetime
from base import MiData


def load_mat(data_path):
    """
    Load data from a .mat file

    Parameters
    ----------
    data_path : str
        Path of .mat format data

    Returns
    -------
    signal_data : list
        List of n arrays, each dimension is one row (channel) data
    channel_name : list
        Name for each channel
    sf : list
        Sampling frequency of each channel
    """

    raw_data = list(loadmat(data_path).values())[-1]
    try:
        # Whether save with python, because python has no 'cell' type
        _ = raw_data['save']
        channels = list(raw_data['channels'][0, 0])
        channels = [each.strip() for each in channels]
        sf = list(raw_data['sf'][0, 0][0].astype(float))
        signals = [raw_data[each][0, 0][0] for each in channels]

        return MiData(signals=signals, channels=channels, sf=sf)
    except ValueError:
        try:
            channels = [item for each in raw_data['channels'][0][0][0] for item in each]
            channels = [each.strip() for each in channels]
            sf = list(raw_data['sf'][0, 0][0].astype(float))
            signals = [raw_data[each][0, 0][0] for each in channels]
        except Exception:
            # If matlab data is not a struct, or have no channel field, will arise this
            signals = raw_data
            channels = [f'ch{each + 1}' for each in range(raw_data.shape[0])]
            sf = [256 for _ in range(raw_data.shape[0])]

            print("We recommend to save signals in different fields and "
                  "channel name/sample frequency save respectively")

        return MiData(signals=signals, channels=channels, sf=sf)


def write_mat(signals, channels, sf, mat_file=None):
    """
    Write data to .mat file

    Parameters
    ----------
    sf : list
        List of int, sampling frequency of each channel in the signal data
    signals : n-D array
    channels : list
    mat_file : str
        Path to save data

    Returns
    -------

    """

    if mat_file is None:
        mat_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.mat"

    mdict = {'data': dict(zip(channels, signals))}
    mdict['data']['save'] = 'python'
    mdict['data']['channels'] = channels
    mdict['data']['sf'] = sf

    savemat(file_name=mat_file, mdict=mdict, format='5')


def load_edf(data_path):
    """
    Load data from .edf file

    Parameters
    ----------
    data_path : str
        Path of .edf data file

    Returns
    -------
    signal_data : ndarray
        Data in n-D array, each dimension is one row (channel) data
    channel_name : list
        Name for each channel
    sf : list
        List of sampling frequency for each channel
    """

    signals, signal_headers, _ = pyedflib.highlevel.read_edf(edf_file=data_path)

    return MiData(signals=signals,
                  channels=[each['label'] for each in signal_headers],
                  sf=[each['sample_frequency'] for each in signal_headers])
