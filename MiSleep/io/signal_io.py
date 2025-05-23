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
from misleep.utils.logger_handler import logger


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
    
    from misleep.io.base import MiData

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
            channels = list(names[:-4])
            sf = [float(each) for each in raw_data['sf'][0]]
            signals = [raw_data[each][0] for each in channels]
            time = raw_data['time'][0]
            return MiData(signals=signals, channels=channels, sf=sf, time=time)

        # Saved by matlab
        channels = [each for item in raw_data['channels'][0] for each in item]
        sf = [float(each[0]) for item in raw_data['sf'][0] for each in item]
        signals = []
        try:
            for each in channels:
                signal_ = raw_data[each]
                if signal_.shape[0] > signal_.shape[1]:
                    signals.append(signal_.T[0])
                if signal_.shape[0] < signal_.shape[1]:
                    signals.append(signal_[0])
        except Exception as e:
            logger.error(f"Load data ERROR: {e}")
            return 
        try:
            time = raw_data['time'][0][0][0]
            datetime.datetime.strptime(time, "%Y%m%d-%H:%M:%S")
        except ValueError as e:
            time = raw_data['time'][0]
        
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
            signals = []
            time = raw_data['time'][0]

            try:
                for each in channels:
                    signal_ = raw_data[each]
                    if signal_.shape[0] > 1:
                        signals.append(signal_)
                    if signal_.shape[0] == 1:
                        signals.append(signal_.T)
            except Exception as e:
                logger.error(f"Load data ERROR: {e}")
                return 

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
                logger.error(f"Load data ERROR: {e}")
                return None  
            
    except Exception as e:
        logger.error(f"Load data ERROR: {e}")
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
    
    from misleep.io.base import MiData

    return MiData(signals=signals,
                  channels=[each['label'] for each in signal_headers],
                  sf=[each['sample_frequency'] for each in signal_headers],
                  time=meta['startdate'].strftime('%Y%m%d-%H:%M:%S'))


def write_edf(signals, channels, sf, time, edf_file=None):
    """
    Write data to an EDF (European Data Format) file.

    This function saves the provided signal data, channel names, sampling frequencies, 
    and start time into an EDF file at the specified file path.

    Parameters
    ----------
    signals : list 
        A list containing the signal data for each channel. Each element 
        corresponds to the signal data for one channel.
    channels : list of str
        A list of channel names corresponding to the signal data.
    sf : list of float
        A list of sampling frequencies for each channel.
    time : str
        The start time of the recording in the format "YYYYMMDD-HH:MM:SS".
    edf_file : str
        The file path where the EDF file will be saved.

    Returns
    -------
    None
        The function writes the data to the specified file and does not return any value.

    Notes
    -----
    - The function assumes that the length of `signals`, `channels`, and `sf` are the same.
    - The `pyedflib` library is used to handle the EDF file writing process.
    - Ensure that the `edf_file` is a valid path where the file can be created.

    Example
    -------
    >>> signals = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    >>> channels = ["EEG1", "EEG2"]
    >>> sf = [256.0, 256.0]
    >>> time = "20250423-12:00:00"
    >>> edf_file = "output.edf"
    >>> write_edf(signals, channels, sf, time, edf_file)
    """
    import pyedflib

    
    if edf_file is None:
        edf_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.edf"

    # Create a dictionary for the EDF header
    header = {'technician': '',
              'recording_additional': '',
              'patientname': 'MiSleep',
              'patient_additional': '',
              'patientcode': '',
              'equipment': '',
              'admincode': '',
              'sex': '',
              'startdate': datetime.datetime.strptime(time, "%Y%m%d-%H:%M:%S"),
              'birthdate': '',
              'gender': '',
              'annotations': []
            }
    
    signal_headers = [
        {'label': each,
            'dimension': 'uV',
            'sample_rate': sf[idx],
            'sample_frequency': sf[idx],
            'physical_max': 10417.0,
            'physical_min': -10417.0,
            'digital_max': 32767,
            'digital_min': -32768,
            'prefilter': '',
            'transducer': ''
        } for idx, each in enumerate(channels)
    ]

    try:

        with pyedflib.EdfWriter(edf_file, len(signals)) as edf_writer:
            # Set the header information
            edf_writer.setHeader(header)

            # Add each signal to the EDF file
            for i, signal in enumerate(signals):
                edf_writer.setSignalHeader(i, signal_headers[i])
            edf_writer.writeSamples(signals)
    
    except Exception as e:
        logger.error(f"Write data ERROR: {e}")
  

