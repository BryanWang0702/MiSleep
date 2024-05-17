# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: annotation.py
@Author: Xueqiang Wang
@Date: 2024/3/6
@Description:  
"""
from itertools import groupby
import datetime 
import pandas as pd


def lst2group(pre_lst):
    """
    Convert a list like [[1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 1], [7, 1], [8, 1], [9, 3], [10, 3]] to
    [[1, 5, 2], [6, 8, 1], [9, 10, 3]]
    :param pre_lst:
    :return:
    """

    # Convert to [[[1, 2], [2, 2], [3, 2], [4, 2], [5, 2]], [[6, 1], [7, 1], [8, 1]], [[9, 3], [10, 3]]]
    pre_lst = [list(group) for _, group in groupby(pre_lst, key=lambda x: x[1])]

    # Convert to [[1, 5, 2], [6, 8, 1], [9, 10, 3]] and then to [[1, 6, 2], [6, 9, 1], [9, 10, 3]]
    return [[each[0][0], each[-1][0]+1, each[0][1]] for each in pre_lst]

def marker2mianno(marker):
    """
    Transfer MiSleep annotation to [[1, 'injection'], 20, 'injection'], ...] format
    """
    if marker != [] or marker is not None:
        marker = [each.split(', ') for each in marker]
        marker = [[float(each[1]), each[7]] for each in marker]
        return marker
    return []


def start_end2mianno(start_end):
    """Transfer start_end to [[1, 20, 'spindle'], [30, 50, 'SWA'], ...]"""
    if start_end != [] or start_end is not None:
        start_end = [each.split(', ') for each in start_end]
        start_end = [[float(each[1]), float(each[4]), each[7]] for each in start_end]
        return start_end
    return []


def sleep_state2mianno(sleep_state):
    """Transfer sleep_state to [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, ...]"""
    start_end = [each.split(', ') for each in sleep_state]
    # Old version misleep label, start from 1
    if start_end[0][1] == '1':
        sleep_state = [item for each in start_end for item in [int(each[6])] * (int(each[4]) - int(each[1]) + 1)]
    else:
        sleep_state = [item for each in start_end for item in [int(each[6])] * (int(each[4]) - int(each[1]))]
    return sleep_state


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
