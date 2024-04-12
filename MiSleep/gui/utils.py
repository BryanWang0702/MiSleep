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