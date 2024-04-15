# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: annotation_io.py
@Author: Xueqiang Wang
@Date: 2024/3/6
@Description:  Annotation io, default is for MiSleep annotation, `NAME.txt`
"""
from misleep.io.base import MiAnnotation
from misleep.utils.annotation import marker2mianno, start_end2mianno, lst2group, sleep_state2mianno, \
    transfer_time, insert_row, temp_loop4below_row
import pandas as pd


def load_misleep_anno(file_path):
    """
    Load annotations from misleep annotation file

    Parameters
    ----------
    file_path : str
        Path of annotation file
    """

    # Read out the annotation file and split by `\n` to get each line
    annotation = open(file_path, 'r').read().split('\n')
    if annotation == [""]:
        raise AssertionError("Empty")
    try:
        marker_idx = annotation.index('==========Marker==========')
        start_end_idx = annotation.index('==========Start-End==========')
        try:
            sleep_state_idx = annotation.index('==========Sleep state==========')
        except ValueError:
            sleep_state_idx = annotation.index('==========Sleep stage==========')
    except Exception:
        raise AssertionError("Invalid")

    marker = annotation[marker_idx + 1: start_end_idx]
    marker = marker2mianno(marker)

    start_end = annotation[start_end_idx + 1: sleep_state_idx]
    start_end = start_end2mianno(start_end)

    sleep_state = annotation[sleep_state_idx + 1:]
    sleep_state = sleep_state2mianno(sleep_state)

    return MiAnnotation(sleep_state=sleep_state, start_end=start_end, marker=marker)


def load_bio_anno(file_path):
    """Load bio-signal annotation"""
    file = open(file_path, 'r').readlines()
    file = file[2:]
    state_list = [each.split('\t')[1] for each in file]
    state_list = [[each]*4 for each in state_list]
    state_list = [item for each in state_list for item in each]
    state_map = {
        'AW': 3,
        'QW': 3,
        'NREM': 1,
        'REMS': 2
    }

    state_list = [state_map[each] for each in state_list]
    return MiAnnotation(sleep_state=state_list, marker=[], start_end=[])


def transfer_result(mianno, ac_time):
    marker = [[
        transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S'), 
        each[0], each[1]] for each in mianno.marker]

    start_end_label = [[
        transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S', ms=True), each[0], 1,
        transfer_time(ac_time, each[1], '%Y-%m-%d %H:%M:%S', ms=True), each[1], 0,
        each[2]
    ] for each in mianno.start_end]

    sleep_state = lst2group([[idx+1, each] 
                                for idx, each in enumerate(mianno.sleep_state)])
    sleep_state = [[
        transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S'), each[0], 1,
        transfer_time(ac_time, each[1], '%Y-%m-%d %H:%M:%S'), each[1], 0,
        each[2], mianno.state_map[each[2]]
    ] for each in sleep_state]

    columns=['start_time', 'start_time_sec', 'start_code',
                'end_time', 'end_time_sec', 'end_code',
                'state_code', 'state']

    df = pd.DataFrame(data=sleep_state, columns=columns)
    
    new_df = pd.DataFrame(columns=columns)
    for idx, row in df.iterrows():
        if row['end_time_sec'] % 3600 == 0:
            new_df = insert_row(new_df, idx, row)
            # Just add a row and nothing else
            new_row = pd.Series([
                row['end_time'], row['end_time_sec'], ' ',
                row['end_time'], row['end_time_sec'], '5',
                ' ', 'MARKER'
            ], index=columns)
            new_df = insert_row(new_df, new_df.shape[0], new_row)
            continue

        if int(row['end_time_sec'] / 3600) > int(row['start_time_sec'] / 3600):

            previous_row, new_row, below_row = temp_loop4below_row(row, ac_time, columns)

            new_df = insert_row(new_df, new_df.shape[0], previous_row)
            new_df = insert_row(new_df, new_df.shape[0], new_row)
            while int(below_row['end_time_sec'] / 3600) > int(below_row['start_time_sec'] / 3600):
                row = below_row
                previous_row, new_row, below_row = temp_loop4below_row(row, ac_time, columns)
                new_df = insert_row(new_df, new_df.shape[0], previous_row)
                new_df = insert_row(new_df, new_df.shape[0], new_row)

            new_df = insert_row(new_df, new_df.shape[0], below_row)
            continue

        new_df = insert_row(new_df, new_df.shape[0], row)

    df = new_df
    del new_df

    df['bout_duration'] = df.apply(
        lambda x: x[4] - x[1] + 1 if x[7] != 'MARKER' else '', axis=1)
    
    df['hour'] = df['start_time_sec'].apply(lambda x: int(x / 3600) if x % 3600 != 0 else '')
    analyse_df = pd.DataFrame()

    temp_hour = list(set(list(df['hour'])))
    temp_hour.remove('')
    temp_hour = sorted(temp_hour)
    analyse_df['date_time'] = [transfer_time(ac_time, each*3600, "%Y-%m-%d %H:%M:%S")
                            for each in temp_hour]

    features = []
    for each in temp_hour:
        df_ = df[df['hour'] == each]
        temp_lst = []
        for phase in ["NREM", "REM", "Wake", "INIT"]:
            _duration = df_[df_["state"] == phase]["bout_duration"].sum()
            _bout = df_[df_["state"] == phase]["bout_duration"].count()
            temp_lst += [_duration, _bout, round(_duration / _bout, 2) if _bout != 0 else 0, round(_duration / 3600, 2)]
        features.append(temp_lst)

    analyse_df[['NREM_duration', 'NREM_bout', "NREM_ave", "NREM_percentage",
                'REM_duration', 'REM_bout', "REM_ave", "REM_percentage",
                'WAKE_duration', 'WAKE_bout', "WAKE_ave", "WAKE_percentage",
                'INIT_duration', 'INIT_bout', "INIT_ave", "INIT_percentage"]] = features


    analyse_df[
        ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
        'WAKE_bout', 'INIT_duration', 'INIT_bout']
    ] = analyse_df[
        ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
        'WAKE_bout', 'INIT_duration', 'INIT_bout']].astype(int)
    
    return df, analyse_df

