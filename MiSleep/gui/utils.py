from misleep.io.base import MiAnnotation

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