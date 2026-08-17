# -*- coding: UTF-8 -*-
"""Data model module.

This module contains the in-memory data containers used across MiSleep:

* :class:`misleep.data.midata.MiData` -- raw signal recordings
* :class:`misleep.data.annotation.MiAnnotation` -- sleep scoring/annotation
"""

from .midata import MiData
from .annotation import MiAnnotation

__all__ = ["MiData", "MiAnnotation"]
