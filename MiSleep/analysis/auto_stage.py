import misleep
import numpy as np
from math import floor
import pandas as pd
from scipy import stats
import antropy
import joblib
import copy


def filter_power_line_noise(data, sf, noise_band='50-100-150'):
    """Use 50-100-150 Hz bandstop filter to filter the power line noise
    The noise band can be '50-100-150' or '60-120-180'
    TODO: add the 60-120-180 band
    """
    filter_band = []
    if noise_band == '50-100-150' and sf > 306:
        filter_band = [[47, 53], [97, 103], [147, 153]]
    elif noise_band == '50-100-150' and sf > 206:
        filter_band = [[47, 53], [97, 103]]
    elif sf > 106:
        filter_band = [[47, 53]]
    for each in filter_band:
        data, _ = misleep.signal_filter(data, sf, btype='bandstop', low=each[0], high=each[1])
    
    return data

def split_window_data(data, sf, state, window_length=20, stride_length=5):
    """Split the data into several windows with the window length
    window length is in seconds, so we need the sampling frequency (sf) to locate the data point,
    stride length is the step
    Also contain the state information within the data
    """

    # If the data is shorter than the window length, remove it
    if data.shape[0]/sf < 20:
        return []
    
    window_data = []
    # Make sure we have enough data point of the final segment
    data_sec_length = floor(data.shape[0] / sf)
    for i in range(0, data_sec_length-stride_length, stride_length):
        window = data[int(i*sf):int((i+window_length)*sf)]
        window_data.append([window, state])

    return window_data

def delta_theta_ratio(data, sf):
    """Calculate the delta/theta ratio from the original signal data
    Note, here the data is 20 seconds, we only need the ratio from the 5 seconds beginning
    """
    freq, t, Sxx = misleep.spectrogram(data, sf, window=1)
    band_second = np.where(t < 5)
    psd = np.sum(np.array([each[band_second] for each in Sxx]), axis=1)
    band_power = misleep.band_power(psd, freq, bands=[[0.5, 4, 'delta'], [5, 9, 'theta']])
    return band_power['delta'] / band_power['theta']

def get_data_features(data, sf, data_format='EEG'):
    """ Get data features, data format can be 'EEG' or 'EMG'
    data: list of window signal data, [[signal_array(20s), signal_label], ...]
    """

    # Extract the time-domain and frequency domain features from window data, use a dataframe to store all the features
    window_feature_df = pd.DataFrame()
    window_feature_df['label'] = [each[1] for each in data]

    # Time-domain features, both EEG and EMG
    # 1. standard deviation
    data_std = np.array([np.std(each[0][:int(5*sf)]) for each in data])
    # Set those abnormal points to the upper quartile
    data_std_upper_quantile = np.quantile(data_std, 0.95)
    data_std = [each if each < data_std_upper_quantile else data_std_upper_quantile for each in data_std]
    # Z-score the std features
    window_feature_df[f'{data_format}_std_zscore'] = (data_std - np.mean(data_std)) / np.std(data_std)
    
    # 2. Zero crossing rate for EEG and EMG
    zerocross_rate = [antropy.num_zerocross(each[0][:int(5*sf)]) / (5*sf) for each in data]
    window_feature_df[f'{data_format}_zerocross_rate'] = (zerocross_rate - np.mean(zerocross_rate)) / np.std(zerocross_rate)

    # 3. Hjorth parameters -- Mobility and Complexity
    hjorth = [antropy.hjorth_params(each[0][:int(5*sf)]) for each in data]
    hjorth_M = [each[0] for each in hjorth]
    hjorth_C = [each[1] for each in hjorth]
    window_feature_df[f'{data_format}_Hjorth_M'] = (hjorth_M - np.mean(hjorth_M)) / np.std(hjorth_M)
    window_feature_df[f'{data_format}_Hjorth_C'] = (hjorth_C - np.mean(hjorth_C)) / np.std(hjorth_C)

    # 4. Permutation entropy
    perm_entropy= [antropy.perm_entropy(each[0][:int(5*sf)]) for each in data]
    window_feature_df[f'{data_format}_perm_entropy'] = (perm_entropy - np.mean(perm_entropy)) / np.std(perm_entropy) 

    # Some features only with EEG
    if data_format.startswith('EEG'):
        # 1. Skewness and kurtosis for EEG signal(s)
        data_skewness = np.array([stats.skew(each[0][:int(5*sf)]) for each in data])
        data_kurtosis = np.array([stats.kurtosis(each[0][:int(5*sf)]) for each in data])
        window_feature_df[f'{data_format}_skewness_zscore'] = (data_skewness - np.mean(data_skewness)) / np.std(data_skewness)
        window_feature_df[f'{data_format}_kurtosis_zscore'] = (data_kurtosis - np.mean(data_kurtosis)) / np.std(data_kurtosis)
        # Frequency-domain features
        # 1. delta/theta
        delta_theta = [delta_theta_ratio(each[0], sf) for each in data]
        window_feature_df[f'{data_format}_delta_theta'] = (delta_theta - np.mean(delta_theta)) / np.std(delta_theta) 

    return window_feature_df

def result_constraints(pred_label):
    """
    Once finished the prediction, add some constraints to make the result more smooth
    1. No REM after Wake, set to NREM
    2. All one epoch between two same state will be set to the around state
    """

    pred_label = copy.deepcopy(pred_label)
    for idx in range(1, len(pred_label)-1):
        label_ = pred_label[idx]
        if label_ == 3 and pred_label[idx+1] == 2:  # REM after Wake
            pred_label[idx+1] = 1
        if pred_label[idx-1] ==pred_label[idx+1]:  # Same state previous and after
            pred_label[idx] = pred_label[idx-1]
    
    return pred_label


def auto_stage_gbm(EEG, EMG, sf, EEG_channel='F'):
    """
    Auto stage with lightgbm method
    
    Parameters
    ----------
    EEG : array
        EEG data for auto stage. For channel specify, see EEG_channel.
    EMG : array
        EMG data for auto stage.
    sf : double
        Sampling frequency of the EEG and EMG data, should be the same.
    EEG_channel : string
        Specify the channel of EEG, frontal or parietal. Options: {'F', 'P'}. Default is 'F' for frontal.

    Return
    ------
    pred_label : list
        Predicted labels for every second. May less than the data length for about 15 seconds.
    """ 
    EEG = split_window_data(EEG, sf, state=4)  # All set the initial state '4'
    EMG = split_window_data(EMG, sf, state=4)

    window_feature_df = pd.DataFrame()
    window_feature_df = pd.concat([get_data_features(EEG, sf, data_format='EEG'), get_data_features(EMG, sf, data_format='EMG')], axis=1)
    window_feature_df = window_feature_df.filter(like='E')

    if EEG_channel == 'F':
        gbm_model = joblib.load(r'./misleep/analysis/auto_stage_model/EEG_F_lightgbm_20241221.pkl')
    if EEG_channel == 'P':
        gbm_model = joblib.load(r'./misleep/analysis/auto_stage_model/EEG_P_lightgbm_20241221.pkl')

    pred_label = gbm_model.predict(window_feature_df, num_iteration=gbm_model.best_iteration_)
    pred_label = result_constraints(pred_label)
    pred_label = [item for each in pred_label for item in [each]*5]
    return pred_label
