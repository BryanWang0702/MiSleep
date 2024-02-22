# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/21
@Description:  Load data from data file and write data into file
                Support .mat, .edf, .npz currently

                Load functions will return the signal data and the name for each channel:
                signal_data, channel_names, sf

                Write functions require a n-D data array for input and
                a list for channel name (optional)
"""

from hdf5storage import loadmat, savemat
import pyedflib
import datetime
import numpy as np


def load_mat(data_path):
    """
    Load data from a .mat file

    Parameters
    ----------
    data_path : str
        Path of .mat format data

    Returns
    -------
    signal_data : ndarray
        Data in n-D array, each dimension is one row (channel) data
    channel_name : list
        Name for each channel
    """

    raw_data = list(loadmat(data_path).values())[-1]
    try:
        signals = raw_data['signals'][0, 0]
        channels = [item for each in raw_data['channels'][0][0][0] for item in each]
        channels = [each.strip() for each in channels]
    except Exception:
        # If matlab data is not a struct, or have no channel field, will arise this
        signals = raw_data
        channels = [f'ch{each+1}' for each in range(raw_data.shape[0])]

        print("We recommend to save signals in the 'signals' field, "
              "and each signal's name in the 'channels' field")
    if signals.shape[0] > signals.shape[1]:
        signals = signals.T

    if len(channels) > signals.shape[0]:
        channels = channels[:signals.shape[0]]
    elif len(channels) < signals.shape[0]:
        for i in range(len(channels), signals.shape[0]):
            channels.append(f'ch{i+1}')

    return signals, channels


def write_mat(signals, channels, mat_file=None):
    """
    Write data to .mat file

    Parameters
    ----------
    signals : n-D array
    channels : list
    mat_file : str
        Path to save data

    Returns
    -------

    """

    if mat_file is None:
        mat_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.mat"

    mdict = {
        'data': {
            'signals': signals,
            'channels': channels,
        }
    }

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
    """

    signals, signal_headers, _ = pyedflib.highlevel.read_edf(edf_file=data_path)

    return np.array(signals), [each['label'] for each in signal_headers]


def write_edf(signals, channels, sf, edf_file=None):
    """
    Write data to .edf file

    Parameters
    ----------
    sf : int
        Sampling frequency
    signals :
    channels :
    edf_file :

    Returns
    -------

    """
    if edf_file is None:
        edf_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.edf"

    # Construct the header with channels information
    signal_headers = [{
            'label': ch,
            'dimension': 'uV',
            'sample_rate': sf,
            'physical_max': 5000,
            'physical_min': -5000,
            'digital_max': 32767,
            'digital_min': -32768,
            'transducer': '',
            'prefilter': ''
        } for ch in channels]

    pyedflib.highlevel.write_edf(edf_file=edf_file, signals=signals,
                                 signal_headers=signal_headers)


def load_npz(data_path):
    """
    Load data from .npz file, which was stored with numpy
    Why npz not npy? We need to store signals and channels respectively, .npz can do this
    Parameters
    ----------
    data_path :

    Returns
    -------

    """

    npy_data = np.load(data_path)
    try:
        signals = npy_data['signals']
        channels = npy_data['channels']

        return signals, channels
    except KeyError:
        print('Ensure your .npz data was stored by MiSleep')
        return


def write_npz(signals, channels, npz_file=None):
    """
    Write data into .npz file
    Parameters
    ----------
    signals :
    channels :
    npz_file :

    Returns
    -------

    """
    if npz_file is None:
        npz_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.npz"

    np.savez(npz_file, signals=signals, channels=channels)
