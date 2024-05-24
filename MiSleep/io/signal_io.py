# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/21
@Description:   Load data from .mat or .edf file, write data into .mat file
                Data contains: Signals, channel name, sampling frequency

                20240228: Use MiData format for the final output
"""

from hdf5storage import savemat
import pyedflib
import datetime
from misleep.io.base import MiData


def load_mat(data_path):
    """
    Load data from a .mat file

    Mat file got three version, v5.7 and v7.3 from matlab and python saved file, 
    when the mat file is larger than 2 GB, Matlab will suggest to store as v7.3, 
    while ``scipy.io.loadmat`` can't load v7.3 mat file, 
    use mat73 for v7.3 matfile load. When matfile was saved by python, there is
    no ``cell`  type, so use `save` argument to identify

    Parameters
    ----------
    data_path : str
        Path of .mat format data

    Returns
    -------
    midata : MiData
        MiSleep data format data
    """

    from scipy.io import loadmat as scipy_loadmat
    from mat73 import loadmat as mat73_loadmat

    try:
        # Use scipy to load
        raw_data = list(scipy_loadmat(data_path).values())[-1]
        names = raw_data.dtype.names

        # If old version misleep data
        if names is None:
            if raw_data.shape[0] > raw_data.shape[1]:
                signals = raw_data.T
            else:
                signals = raw_data
            channels = [f'ch{each + 1}' for each in range(signals.shape[0])]
            sf = [305. for _ in range(signals.shape[0])]
            time = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
            return MiData(signals=signals, channels=channels, sf=sf, time=time)

        raw_data = raw_data[0][0]
        # Whether saved by python
        if 'save' in names:
            channels = list(raw_data['channels'])
            sf = [float(each) for each in raw_data['sf'][0]]
            signals = [raw_data[each][0] for each in channels]
            time = raw_data['time'][0]
            return MiData(signals=signals, channels=channels, sf=sf, time=time)

        # Saved by matlab
        channels = [each for item in raw_data['channels'][0] for each in item]
        sf = [float(each[0]) for item in raw_data['sf'][0] for each in item]
        signals = [raw_data[each][0] for each in channels]
        try:
            time = raw_data['time'][0][0][0]
            datetime.datetime.strptime(time, "%Y%m%d-%H:%M:%S")
        except ValueError:
            time = raw_data['time'][0]

        try:
            for idx, each in enumerate(signals):
                if each.shape[0] > each.shape[1]:
                    each = each.T
                    signals[idx] = each
        except Exception:
            pass
        
        return MiData(signals=signals, channels=channels, sf=sf, time=time)
    
    except NotImplementedError:
        # The mat file is v7.3, use mat73 to load
        raw_data = list(mat73_loadmat(data_path).values())[-1]

        try:
            _ = raw_data['channels']
            if 'save' in raw_data.keys():
                # Saved by python
                pass

            channels = raw_data['channels']
            sf = [float(each) for each in raw_data['sf']]
            signals = [raw_data[each] for each in channels]
            time = raw_data['time'][0]

            try:
                for idx, each in enumerate(signals):
                    if each.shape[0] > each.shape[1]:
                        each = each.T
                        signals[idx] = each
            except Exception:
                pass

            return MiData(signals=signals, channels=channels, sf=sf, time=time)
    
        except Exception:
            # If old version misleep data
            try:
                if raw_data.shape[0] > raw_data.shape[1]:
                    signals = raw_data.T
                else:
                    signals = raw_data
                
                channels = [f'ch{each + 1}' for each in range(signals.shape[0])]
                sf = [305. for _ in range(signals.shape[0])]
                time = datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")
                return MiData(signals=signals, channels=channels, sf=sf, time=time)
            except Exception as e:
                print(e)
                return None  
            
    except Exception as e:
        print(e)
        return None


def write_mat(signals, channels, sf, time, mat_file=None):
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
    mdict['data']['time'] = time

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
    midata : MiData
        MiSleep data format data
    """

    signals, signal_headers, meta = pyedflib.highlevel.read_edf(edf_file=data_path)

    return MiData(signals=signals,
                  channels=[each['label'] for each in signal_headers],
                  sf=[each['sample_frequency'] for each in signal_headers],
                  time=meta['startdate'].strftime('%Y%m%d-%H:%M:%S'))
