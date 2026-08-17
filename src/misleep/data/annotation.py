# -*- coding: UTF-8 -*-
"""Core annotation container :class:`MiAnnotation`.

A :class:`MiAnnotation` stores everything the user scores for one
recording:

* the per-second **sleep state** sequence (1 = NREM, 2 = REM, 3 = Wake,
  4 = Init by default, but fully configurable through ``state_map``),
* single time-point **markers** (e.g. ``[30.5, 'injection']``),
* **start-end** events (e.g. ``[1, 20, 'spindle']``).
"""


class MiAnnotation:
    """MiSleep annotation class.

    Default state mapping::

        1 -- NREM
        2 -- REM
        3 -- Wake
        4 -- Init

    Parameters
    ----------
    sleep_state : list
        Per-second sleep state labels. The length of ``sleep_state`` equals
        the total duration (in seconds) of the recording. Every element must
        be a key of ``state_map``.
    marker : list, optional
        Single time-point events, e.g. ``[[1, 'injection'], [30, 'injection']]``.
    start_end : list, optional
        Start-end events, e.g. ``[[1, 20, 'spindle'], [30, 50, 'SWA']]``.
    state_map : dict, optional
        Mapping from state code to its meaning. Defaults to
        ``{1: 'NREM', 2: 'REM', 3: 'Wake', 4: 'Init'}``.
    """

    def __init__(self, sleep_state, marker=None, start_end=None, state_map=None):
        if not isinstance(sleep_state, list):
            raise TypeError(f"'sleep_state' should be a list, got {type(sleep_state)}")

        if state_map is None:
            self._state_map = {1: "NREM", 2: "REM", 3: "Wake", 4: "Init"}
        else:
            self._state_map = state_map

        for each in sleep_state:
            if each not in self._state_map.keys():
                raise ValueError(f"Content {each} in the 'sleep_state' does not exist in {self._state_map}")

        self._sleep_state = sleep_state
        self._anno_length = len(sleep_state)

        if marker is not None:
            if not isinstance(marker, list):
                raise TypeError(f"'marker' should be a list, got {type(marker)}")
        self._marker = marker if marker is not None else []

        if start_end is not None:
            if not isinstance(start_end, list):
                raise TypeError(f"'start_end' should be a list, got {type(start_end)}")
        self._start_end = start_end if start_end is not None else []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def sleep_state(self, time_period=None):
        """Per-second sleep state labels.

        Parameters
        ----------
        time_period : list of two ints, optional
            Crop the returned sequence to ``[start, end]`` seconds.
        """
        if time_period is None:
            return self._sleep_state
        return self._sleep_state[time_period[0]: time_period[1]]

    @property
    def marker(self, time_period=None):
        """Marker events, optionally restricted to a time window."""
        if time_period is None:
            return self._marker
        return [each for each in self._marker if time_period[0] <= each[0] <= time_period[1]]

    @property
    def start_end(self, time_period=None):
        """Start-end events, optionally restricted to a time window."""
        if time_period is None:
            return self._start_end
        return [each for each in self._start_end if time_period[0] <= each[0] and each[1] <= time_period[1]]

    @property
    def anno_length(self):
        """Length of the annotation in seconds."""
        return self._anno_length

    @property
    def state_map(self):
        """Mapping from state code to state name."""
        return self._state_map

    @property
    def state_names(self):
        """Sorted list of state names used in this annotation."""
        return [self._state_map[k] for k in sorted(self._state_map)]

    def __repr__(self):
        return (f"MiAnnotation(length={self._anno_length}s, "
                f"markers={len(self._marker)}, "
                f"start_end={len(self._start_end)}, "
                f"state_map={self._state_map})")
