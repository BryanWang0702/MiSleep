# -*- coding: UTF-8 -*-
"""Utility module.

Pure-Python helpers that do not depend on the GUI or the data containers:

* :mod:`misleep.utils.annotation`  -- annotation line <-> list conversion
* :mod:`misleep.utils.time_utils`  -- datetime helpers
* :mod:`misleep.utils.entropy`     -- signal complexity measures
* :mod:`misleep.utils.misc`        -- various small helpers
"""

from .annotation import (
    lst2group,
    marker2mianno,
    start_end2mianno,
    sleep_state2mianno,
    insert_row,
    temp_loop4below_row,
)
from .time_utils import transfer_time, second2time
from .entropy import num_zerocross, hjorth_params, perm_entropy
from .misc import (
    create_new_mianno,
    identify_startend_color,
    get_base_path,
    downsample_by_most_frequent,
)

__all__ = [
    "lst2group",
    "marker2mianno",
    "start_end2mianno",
    "sleep_state2mianno",
    "insert_row",
    "temp_loop4below_row",
    "transfer_time",
    "second2time",
    "num_zerocross",
    "hjorth_params",
    "perm_entropy",
    "create_new_mianno",
    "identify_startend_color",
    "get_base_path",
    "downsample_by_most_frequent",
]
