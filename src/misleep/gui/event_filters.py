# -*- coding: UTF-8 -*-
"""App-wide Qt event filters.

* :class:`WheelInputGuard` -- stops the mouse wheel from changing values
  of spin boxes / combo boxes / date-time editors (avoids accidental
  edits when scrolling over a control).
"""

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QComboBox


class WheelInputGuard(QObject):
    """Swallow wheel events that land on numeric/date/choice editors."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            widget = QApplication.widgetAt(event.globalPosition().toPoint())
            if widget is not None and isinstance(widget, (QAbstractSpinBox, QComboBox)):
                return True  # consume: do not change the value
        return False
