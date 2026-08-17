# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDateTimeEdit, QDockWidget, QDoubleSpinBox, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QMainWindow, QMenu,
    QMenuBar, QPushButton, QRadioButton, QScrollArea,
    QScrollBar, QSizePolicy, QSpinBox, QTabWidget,
    QWidget)
from misleep.gui.resources import misleep_rc

class Ui_MiSleep(object):
    def setupUi(self, MiSleep):
        if not MiSleep.objectName():
            MiSleep.setObjectName(u"MiSleep")
        MiSleep.resize(1451, 971)
        MiSleep.setFocusPolicy(Qt.WheelFocus)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MiSleep.setWindowIcon(icon)
        MiSleep.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        MiSleep.setAnimated(True)
        MiSleep.setDocumentMode(True)
        MiSleep.setTabShape(QTabWidget.Rounded)
        MiSleep.setDockNestingEnabled(False)
        MiSleep.setDockOptions(QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.GroupedDragging)
        self.actionLoadData = QAction(MiSleep)
        self.actionLoadData.setObjectName(u"actionLoadData")
        self.actionLoadAnnotation = QAction(MiSleep)
        self.actionLoadAnnotation.setObjectName(u"actionLoadAnnotation")
        self.actionAddLine = QAction(MiSleep)
        self.actionAddLine.setObjectName(u"actionAddLine")
        self.actionStateSpectral = QAction(MiSleep)
        self.actionStateSpectral.setObjectName(u"actionStateSpectral")
        self.actionTransferResult = QAction(MiSleep)
        self.actionTransferResult.setObjectName(u"actionTransferResult")
        self.actionAbout = QAction(MiSleep)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSWA_detection = QAction(MiSleep)
        self.actionSWA_detection.setObjectName(u"actionSWA_detection")
        self.actionSpindle_Detection = QAction(MiSleep)
        self.actionSpindle_Detection.setObjectName(u"actionSpindle_Detection")
        self.actionLoad_AccuSleep_Data = QAction(MiSleep)
        self.actionLoad_AccuSleep_Data.setObjectName(u"actionLoad_AccuSleep_Data")
        self.actionSaveData = QAction(MiSleep)
        self.actionSaveData.setObjectName(u"actionSaveData")
        self.actionLightGBM = QAction(MiSleep)
        self.actionLightGBM.setObjectName(u"actionLightGBM")
        self.actionCausalTransformer = QAction(MiSleep)
        self.actionCausalTransformer.setObjectName(u"actionCausalTransformer")
        self.actionConfig = QAction(MiSleep)
        self.actionConfig.setObjectName(u"actionConfig")
        self.centralwidget = QWidget(MiSleep)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.HypnoArea = QScrollArea(self.centralwidget)
        self.HypnoArea.setObjectName(u"HypnoArea")
        self.HypnoArea.setMinimumSize(QSize(0, 120))
        self.HypnoArea.setMaximumSize(QSize(16777215, 130))
        self.HypnoArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 1069, 128))
        self.HypnoArea.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_3.addWidget(self.HypnoArea, 2, 0, 1, 1)

        self.SignalArea = QScrollArea(self.centralwidget)
        self.SignalArea.setObjectName(u"SignalArea")
        self.SignalArea.setMinimumSize(QSize(700, 500))
        self.SignalArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1069, 756))
        self.SignalArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.SignalArea, 0, 0, 1, 1)

        self.ScrollerBar = QScrollBar(self.centralwidget)
        self.ScrollerBar.setObjectName(u"ScrollerBar")
        self.ScrollerBar.setTracking(False)
        self.ScrollerBar.setOrientation(Qt.Horizontal)

        self.gridLayout_3.addWidget(self.ScrollerBar, 1, 0, 1, 1)

        MiSleep.setCentralWidget(self.centralwidget)
        self.MetaDock = QDockWidget(MiSleep)
        self.MetaDock.setObjectName(u"MetaDock")
        self.MetaDock.setMinimumSize(QSize(347, 134))
        self.MetaDock.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.formLayout = QFormLayout(self.dockWidgetContents_3)
        self.formLayout.setObjectName(u"formLayout")
        self.label_4 = QLabel(self.dockWidgetContents_3)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.DataPathEdit = QLineEdit(self.dockWidgetContents_3)
        self.DataPathEdit.setObjectName(u"DataPathEdit")
        self.DataPathEdit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.DataPathEdit)

        self.AnnotationPathLabel = QLabel(self.dockWidgetContents_3)
        self.AnnotationPathLabel.setObjectName(u"AnnotationPathLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.AnnotationPathLabel)

        self.AnnoPathEdit = QLineEdit(self.dockWidgetContents_3)
        self.AnnoPathEdit.setObjectName(u"AnnoPathEdit")
        self.AnnoPathEdit.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.AnnoPathEdit)

        self.label_6 = QLabel(self.dockWidgetContents_3)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.AcTimeEdit = QDateTimeEdit(self.dockWidgetContents_3)
        self.AcTimeEdit.setObjectName(u"AcTimeEdit")
        self.AcTimeEdit.setEnabled(True)
        self.AcTimeEdit.setReadOnly(True)
        self.AcTimeEdit.setKeyboardTracking(False)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.AcTimeEdit)

        self.MetaDock.setWidget(self.dockWidgetContents_3)
        MiSleep.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.MetaDock)
        self.ChannelDock = QDockWidget(MiSleep)
        self.ChannelDock.setObjectName(u"ChannelDock")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChannelDock.sizePolicy().hasHeightForWidth())
        self.ChannelDock.setSizePolicy(sizePolicy)
        self.ChannelDock.setMinimumSize(QSize(318, 487))
        self.ChannelDock.setLayoutDirection(Qt.LeftToRight)
        self.ChannelDock.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.gridLayout = QGridLayout(self.dockWidgetContents_4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line_2 = QFrame(self.dockWidgetContents_4)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 10, 0, 1, 3)

        self.PercentileSpin = QDoubleSpinBox(self.dockWidgetContents_4)
        self.PercentileSpin.setObjectName(u"PercentileSpin")
        self.PercentileSpin.setDecimals(1)
        self.PercentileSpin.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.PercentileSpin, 1, 1, 1, 1)

        self.FilterConfirmBt = QPushButton(self.dockWidgetContents_4)
        self.FilterConfirmBt.setObjectName(u"FilterConfirmBt")

        self.gridLayout.addWidget(self.FilterConfirmBt, 9, 0, 1, 3)

        self.FilterHighSpin = QDoubleSpinBox(self.dockWidgetContents_4)
        self.FilterHighSpin.setObjectName(u"FilterHighSpin")
        self.FilterHighSpin.setKeyboardTracking(False)
        self.FilterHighSpin.setDecimals(1)
        self.FilterHighSpin.setMinimum(0.200000000000000)
        self.FilterHighSpin.setMaximum(10000.000000000000000)
        self.FilterHighSpin.setSingleStep(0.100000000000000)
        self.FilterHighSpin.setValue(30.000000000000000)

        self.gridLayout.addWidget(self.FilterHighSpin, 8, 2, 1, 1)

        self.ShiftDownBt = QPushButton(self.dockWidgetContents_4)
        self.ShiftDownBt.setObjectName(u"ShiftDownBt")

        self.gridLayout.addWidget(self.ShiftDownBt, 13, 2, 1, 1)

        self.label_2 = QLabel(self.dockWidgetContents_4)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 13, 0, 1, 1)

        self.line_3 = QFrame(self.dockWidgetContents_4)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_3, 14, 0, 1, 3)

        self.FilterTypeCombo = QComboBox(self.dockWidgetContents_4)
        self.FilterTypeCombo.addItem("")
        self.FilterTypeCombo.addItem("")
        self.FilterTypeCombo.addItem("")
        self.FilterTypeCombo.addItem("")
        self.FilterTypeCombo.setObjectName(u"FilterTypeCombo")

        self.gridLayout.addWidget(self.FilterTypeCombo, 8, 0, 1, 1)

        self.PlotSpecBt = QPushButton(self.dockWidgetContents_4)
        self.PlotSpecBt.setObjectName(u"PlotSpecBt")

        self.gridLayout.addWidget(self.PlotSpecBt, 15, 0, 1, 3)

        self.ScalerDownBt = QPushButton(self.dockWidgetContents_4)
        self.ScalerDownBt.setObjectName(u"ScalerDownBt")

        self.gridLayout.addWidget(self.ScalerDownBt, 11, 2, 1, 1)

        self.ShiftUpBt = QPushButton(self.dockWidgetContents_4)
        self.ShiftUpBt.setObjectName(u"ShiftUpBt")

        self.gridLayout.addWidget(self.ShiftUpBt, 13, 1, 1, 1)

        self.FilterLowSpin = QDoubleSpinBox(self.dockWidgetContents_4)
        self.FilterLowSpin.setObjectName(u"FilterLowSpin")
        self.FilterLowSpin.setKeyboardTracking(False)
        self.FilterLowSpin.setDecimals(1)
        self.FilterLowSpin.setMinimum(0.200000000000000)
        self.FilterLowSpin.setMaximum(10000.000000000000000)
        self.FilterLowSpin.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.FilterLowSpin, 8, 1, 1, 1)

        self.HideChBt = QPushButton(self.dockWidgetContents_4)
        self.HideChBt.setObjectName(u"HideChBt")

        self.gridLayout.addWidget(self.HideChBt, 6, 1, 1, 1)

        self.MultipleScalerConfirmBt = QPushButton(self.dockWidgetContents_4)
        self.MultipleScalerConfirmBt.setObjectName(u"MultipleScalerConfirmBt")

        self.gridLayout.addWidget(self.MultipleScalerConfirmBt, 12, 2, 1, 1)

        self.ScalerUpBt = QPushButton(self.dockWidgetContents_4)
        self.ScalerUpBt.setObjectName(u"ScalerUpBt")

        self.gridLayout.addWidget(self.ScalerUpBt, 11, 1, 1, 1)

        self.DeleteChBt = QPushButton(self.dockWidgetContents_4)
        self.DeleteChBt.setObjectName(u"DeleteChBt")

        self.gridLayout.addWidget(self.DeleteChBt, 6, 2, 1, 1)

        self.ShowChBt = QPushButton(self.dockWidgetContents_4)
        self.ShowChBt.setObjectName(u"ShowChBt")

        self.gridLayout.addWidget(self.ShowChBt, 6, 0, 1, 1)

        self.DefaultCh4SpecBt = QPushButton(self.dockWidgetContents_4)
        self.DefaultCh4SpecBt.setObjectName(u"DefaultCh4SpecBt")

        self.gridLayout.addWidget(self.DefaultCh4SpecBt, 0, 0, 1, 3)

        self.label_3 = QLabel(self.dockWidgetContents_4)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.MoveChPanel = QWidget(self.dockWidgetContents_4)
        self.MoveChPanel.setObjectName(u"MoveChPanel")
        self.moveChLayout = QHBoxLayout(self.MoveChPanel)
        self.moveChLayout.setSpacing(2)
        self.moveChLayout.setObjectName(u"moveChLayout")
        self.moveChLayout.setContentsMargins(0, 0, 0, 0)
        self.MoveLabel = QLabel(self.MoveChPanel)
        self.MoveLabel.setObjectName(u"MoveLabel")

        self.moveChLayout.addWidget(self.MoveLabel)

        self.MoveUpBt = QPushButton(self.MoveChPanel)
        self.MoveUpBt.setObjectName(u"MoveUpBt")
        self.MoveUpBt.setMinimumSize(QSize(24, 24))
        self.MoveUpBt.setMaximumSize(QSize(24, 24))

        self.moveChLayout.addWidget(self.MoveUpBt)

        self.MoveDownBt = QPushButton(self.MoveChPanel)
        self.MoveDownBt.setObjectName(u"MoveDownBt")
        self.MoveDownBt.setMinimumSize(QSize(24, 24))
        self.MoveDownBt.setMaximumSize(QSize(24, 24))

        self.moveChLayout.addWidget(self.MoveDownBt)


        self.gridLayout.addWidget(self.MoveChPanel, 1, 2, 1, 1)

        self.label = QLabel(self.dockWidgetContents_4)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 11, 0, 1, 1)

        self.line = QFrame(self.dockWidgetContents_4)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 7, 0, 1, 3)

        self.multipleScalerEditor = QDoubleSpinBox(self.dockWidgetContents_4)
        self.multipleScalerEditor.setObjectName(u"multipleScalerEditor")
        self.multipleScalerEditor.setDecimals(3)
        self.multipleScalerEditor.setMinimum(0.001000000000000)
        self.multipleScalerEditor.setMaximum(200.000000000000000)
        self.multipleScalerEditor.setValue(1.000000000000000)

        self.gridLayout.addWidget(self.multipleScalerEditor, 12, 1, 1, 1)

        self.ChListView = QListView(self.dockWidgetContents_4)
        self.ChListView.setObjectName(u"ChListView")
        self.ChListView.setTabKeyNavigation(False)
        self.ChListView.setProperty(u"showDropIndicator", False)
        self.ChListView.setDragEnabled(False)
        self.ChListView.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.ChListView.setDefaultDropAction(Qt.CopyAction)
        self.ChListView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ChListView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.ChListView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.ChListView.setMovement(QListView.Static)
        self.ChListView.setProperty(u"isWrapping", False)

        self.gridLayout.addWidget(self.ChListView, 4, 0, 1, 3)

        self.ChannelDock.setWidget(self.dockWidgetContents_4)
        MiSleep.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ChannelDock)
        self.AnnotationDock = QDockWidget(MiSleep)
        self.AnnotationDock.setObjectName(u"AnnotationDock")
        self.AnnotationDock.setMinimumSize(QSize(353, 191))
        self.AnnotationDock.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.gridLayout_2 = QGridLayout(self.dockWidgetContents_5)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.WakeBt = QPushButton(self.dockWidgetContents_5)
        self.WakeBt.setObjectName(u"WakeBt")

        self.gridLayout_2.addWidget(self.WakeBt, 4, 2, 1, 1)

        self.REMBt = QPushButton(self.dockWidgetContents_5)
        self.REMBt.setObjectName(u"REMBt")

        self.gridLayout_2.addWidget(self.REMBt, 3, 3, 1, 1)

        self.InitBt = QPushButton(self.dockWidgetContents_5)
        self.InitBt.setObjectName(u"InitBt")

        self.gridLayout_2.addWidget(self.InitBt, 4, 3, 1, 1)

        self.LabelBt = QPushButton(self.dockWidgetContents_5)
        self.LabelBt.setObjectName(u"LabelBt")

        self.gridLayout_2.addWidget(self.LabelBt, 1, 3, 1, 1)

        self.StartEndRadio = QRadioButton(self.dockWidgetContents_5)
        self.StartEndRadio.setObjectName(u"StartEndRadio")

        self.gridLayout_2.addWidget(self.StartEndRadio, 1, 2, 1, 1)

        self.line_5 = QFrame(self.dockWidgetContents_5)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_5, 2, 0, 1, 4)

        self.SleepStateRadio = QRadioButton(self.dockWidgetContents_5)
        self.SleepStateRadio.setObjectName(u"SleepStateRadio")

        self.gridLayout_2.addWidget(self.SleepStateRadio, 3, 0, 1, 1)

        self.SaveRowPanel = QWidget(self.dockWidgetContents_5)
        self.SaveRowPanel.setObjectName(u"SaveRowPanel")
        self.saveRowLayout = QHBoxLayout(self.SaveRowPanel)
        self.saveRowLayout.setSpacing(2)
        self.saveRowLayout.setObjectName(u"saveRowLayout")
        self.saveRowLayout.setContentsMargins(0, 0, 0, 0)
        self.SaveLabelBt = QPushButton(self.SaveRowPanel)
        self.SaveLabelBt.setObjectName(u"SaveLabelBt")

        self.saveRowLayout.addWidget(self.SaveLabelBt)

        self.MarkerListBt = QPushButton(self.SaveRowPanel)
        self.MarkerListBt.setObjectName(u"MarkerListBt")

        self.saveRowLayout.addWidget(self.MarkerListBt)

        self.StartEndListBt = QPushButton(self.SaveRowPanel)
        self.StartEndListBt.setObjectName(u"StartEndListBt")

        self.saveRowLayout.addWidget(self.StartEndListBt)


        self.gridLayout_2.addWidget(self.SaveRowPanel, 5, 0, 1, 4)

        self.ExtraStatePanel = QWidget(self.dockWidgetContents_5)
        self.ExtraStatePanel.setObjectName(u"ExtraStatePanel")
        self.extraStateLayout = QGridLayout(self.ExtraStatePanel)
        self.extraStateLayout.setObjectName(u"extraStateLayout")
        self.extraStateLayout.setContentsMargins(0, 0, 0, 0)

        self.gridLayout_2.addWidget(self.ExtraStatePanel, 6, 0, 1, 4)

        self.MarkerRadio = QRadioButton(self.dockWidgetContents_5)
        self.MarkerRadio.setObjectName(u"MarkerRadio")

        self.gridLayout_2.addWidget(self.MarkerRadio, 1, 0, 1, 1)

        self.NREMBt = QPushButton(self.dockWidgetContents_5)
        self.NREMBt.setObjectName(u"NREMBt")

        self.gridLayout_2.addWidget(self.NREMBt, 3, 2, 1, 1)

        self.line_4 = QFrame(self.dockWidgetContents_5)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_4, 1, 1, 1, 1)

        self.AnnotationDock.setWidget(self.dockWidgetContents_5)
        MiSleep.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.AnnotationDock)
        self.TimeDock = QDockWidget(MiSleep)
        self.TimeDock.setObjectName(u"TimeDock")
        self.TimeDock.setMinimumSize(QSize(238, 131))
        self.TimeDock.setAcceptDrops(False)
        self.TimeDock.setAutoFillBackground(True)
        self.TimeDock.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.TimeDock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockWidgetContents_7 = QWidget()
        self.dockWidgetContents_7.setObjectName(u"dockWidgetContents_7")
        self.gridLayout_4 = QGridLayout(self.dockWidgetContents_7)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.DateTimeEdit = QDateTimeEdit(self.dockWidgetContents_7)
        self.DateTimeEdit.setObjectName(u"DateTimeEdit")
        self.DateTimeEdit.setKeyboardTracking(False)

        self.gridLayout_4.addWidget(self.DateTimeEdit, 0, 0, 1, 1)

        self.SecondSpin = QSpinBox(self.dockWidgetContents_7)
        self.SecondSpin.setObjectName(u"SecondSpin")
        self.SecondSpin.setKeyboardTracking(False)

        self.gridLayout_4.addWidget(self.SecondSpin, 0, 1, 1, 1)

        self.ShowRangeCombo = QComboBox(self.dockWidgetContents_7)
        self.ShowRangeCombo.addItem("")
        self.ShowRangeCombo.addItem("")
        self.ShowRangeCombo.addItem("")
        self.ShowRangeCombo.addItem("")
        self.ShowRangeCombo.addItem("")
        self.ShowRangeCombo.setObjectName(u"ShowRangeCombo")

        self.gridLayout_4.addWidget(self.ShowRangeCombo, 1, 0, 1, 2)

        self.SecondNumSpin = QSpinBox(self.dockWidgetContents_7)
        self.SecondNumSpin.setObjectName(u"SecondNumSpin")
        self.SecondNumSpin.setKeyboardTracking(False)
        self.SecondNumSpin.setMinimum(5)

        self.gridLayout_4.addWidget(self.SecondNumSpin, 2, 1, 1, 1)

        self.CustomSecondsCheck = QCheckBox(self.dockWidgetContents_7)
        self.CustomSecondsCheck.setObjectName(u"CustomSecondsCheck")

        self.gridLayout_4.addWidget(self.CustomSecondsCheck, 2, 0, 1, 1)

        self.TimeDock.setWidget(self.dockWidgetContents_7)
        MiSleep.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.TimeDock)
        self.menuBar = QMenuBar(MiSleep)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1451, 26))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuTools = QMenu(self.menuBar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuEvent_Detection = QMenu(self.menuTools)
        self.menuEvent_Detection.setObjectName(u"menuEvent_Detection")
        self.menuAuto_Stage = QMenu(self.menuTools)
        self.menuAuto_Stage.setObjectName(u"menuAuto_Stage")
        self.menuResult = QMenu(self.menuBar)
        self.menuResult.setObjectName(u"menuResult")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MiSleep.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuTools.menuAction())
        self.menuBar.addAction(self.menuResult.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoadData)
        self.menuFile.addAction(self.actionLoadAnnotation)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSaveData)
        self.menuTools.addAction(self.actionAddLine)
        self.menuTools.addAction(self.menuEvent_Detection.menuAction())
        self.menuTools.addAction(self.menuAuto_Stage.menuAction())
        self.menuEvent_Detection.addAction(self.actionSWA_detection)
        self.menuEvent_Detection.addAction(self.actionSpindle_Detection)
        self.menuAuto_Stage.addAction(self.actionLightGBM)
        self.menuAuto_Stage.addAction(self.actionCausalTransformer)
        self.menuResult.addAction(self.actionStateSpectral)
        self.menuResult.addAction(self.actionTransferResult)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionConfig)

        self.retranslateUi(MiSleep)

        QMetaObject.connectSlotsByName(MiSleep)
    # setupUi

    def retranslateUi(self, MiSleep):
        MiSleep.setWindowTitle(QCoreApplication.translate("MiSleep", u"MiSleep", None))
        self.actionLoadData.setText(QCoreApplication.translate("MiSleep", u"Load Data (Shift + D)", None))
        self.actionLoadAnnotation.setText(QCoreApplication.translate("MiSleep", u"Load Annotation (Shift + A)", None))
        self.actionAddLine.setText(QCoreApplication.translate("MiSleep", u"Add Line", None))
        self.actionStateSpectral.setText(QCoreApplication.translate("MiSleep", u"State Spectral", None))
        self.actionTransferResult.setText(QCoreApplication.translate("MiSleep", u"Transfer Result", None))
        self.actionAbout.setText(QCoreApplication.translate("MiSleep", u"About", None))
        self.actionSWA_detection.setText(QCoreApplication.translate("MiSleep", u"SWA Detection", None))
        self.actionSpindle_Detection.setText(QCoreApplication.translate("MiSleep", u"Spindle Detection", None))
        self.actionLoad_AccuSleep_Data.setText(QCoreApplication.translate("MiSleep", u"Load AccuSleep Data", None))
        self.actionSaveData.setText(QCoreApplication.translate("MiSleep", u"Save Data", None))
        self.actionLightGBM.setText(QCoreApplication.translate("MiSleep", u"LightGBM", None))
        self.actionCausalTransformer.setText(QCoreApplication.translate("MiSleep", u"CausalTransformer", None))
        self.actionConfig.setText(QCoreApplication.translate("MiSleep", u"Config", None))
        self.MetaDock.setWindowTitle(QCoreApplication.translate("MiSleep", u"Meta", None))
        self.label_4.setText(QCoreApplication.translate("MiSleep", u"Data path:", None))
        self.AnnotationPathLabel.setText(QCoreApplication.translate("MiSleep", u"Annotation path:", None))
        self.label_6.setText(QCoreApplication.translate("MiSleep", u"Acquisition Time:", None))
        self.AcTimeEdit.setDisplayFormat(QCoreApplication.translate("MiSleep", u"yyyy/MM/dd HH:mm:ss", None))
        self.ChannelDock.setWindowTitle(QCoreApplication.translate("MiSleep", u"Channel", None))
        self.FilterConfirmBt.setText(QCoreApplication.translate("MiSleep", u"Filter", None))
        self.ShiftDownBt.setText(QCoreApplication.translate("MiSleep", u"Down", None))
        self.label_2.setText(QCoreApplication.translate("MiSleep", u"Shift:", None))
        self.FilterTypeCombo.setItemText(0, QCoreApplication.translate("MiSleep", u"BandPass", None))
        self.FilterTypeCombo.setItemText(1, QCoreApplication.translate("MiSleep", u"HighPass", None))
        self.FilterTypeCombo.setItemText(2, QCoreApplication.translate("MiSleep", u"LowPass", None))
        self.FilterTypeCombo.setItemText(3, QCoreApplication.translate("MiSleep", u"BandStop", None))

        self.PlotSpecBt.setText(QCoreApplication.translate("MiSleep", u"Plot spectrum", None))
        self.ScalerDownBt.setText(QCoreApplication.translate("MiSleep", u"-", None))
        self.ShiftUpBt.setText(QCoreApplication.translate("MiSleep", u"Up", None))
        self.HideChBt.setText(QCoreApplication.translate("MiSleep", u"Hide", None))
        self.MultipleScalerConfirmBt.setText(QCoreApplication.translate("MiSleep", u"Apply", None))
        self.ScalerUpBt.setText(QCoreApplication.translate("MiSleep", u"+", None))
        self.DeleteChBt.setText(QCoreApplication.translate("MiSleep", u"Delete", None))
        self.ShowChBt.setText(QCoreApplication.translate("MiSleep", u"Show", None))
        self.DefaultCh4SpecBt.setText(QCoreApplication.translate("MiSleep", u"Default channel for spectrogram", None))
        self.label_3.setText(QCoreApplication.translate("MiSleep", u"Percentile:", None))
        self.MoveLabel.setText(QCoreApplication.translate("MiSleep", u"Move:", None))
#if QT_CONFIG(tooltip)
        self.MoveLabel.setToolTip(QCoreApplication.translate("MiSleep", u"Move the selected channel up / down in the list", None))
#endif // QT_CONFIG(tooltip)
        self.MoveUpBt.setText(QCoreApplication.translate("MiSleep", u"\u25b2", None))
#if QT_CONFIG(tooltip)
        self.MoveUpBt.setToolTip(QCoreApplication.translate("MiSleep", u"Move selected channel up", None))
#endif // QT_CONFIG(tooltip)
        self.MoveDownBt.setText(QCoreApplication.translate("MiSleep", u"\u25bc", None))
#if QT_CONFIG(tooltip)
        self.MoveDownBt.setToolTip(QCoreApplication.translate("MiSleep", u"Move selected channel down", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MiSleep", u"Scaler:", None))
        self.AnnotationDock.setWindowTitle(QCoreApplication.translate("MiSleep", u"Annotation", None))
        self.WakeBt.setText(QCoreApplication.translate("MiSleep", u"3:Wake", None))
        self.REMBt.setText(QCoreApplication.translate("MiSleep", u"2:REM", None))
        self.InitBt.setText(QCoreApplication.translate("MiSleep", u"4:Init", None))
        self.LabelBt.setText(QCoreApplication.translate("MiSleep", u"Label", None))
        self.StartEndRadio.setText(QCoreApplication.translate("MiSleep", u"Start-End", None))
        self.SleepStateRadio.setText(QCoreApplication.translate("MiSleep", u"Sleep state", None))
        self.SaveLabelBt.setText(QCoreApplication.translate("MiSleep", u"Save annotation", None))
        self.MarkerListBt.setText(QCoreApplication.translate("MiSleep", u"Marker list", None))
#if QT_CONFIG(tooltip)
        self.MarkerListBt.setToolTip(QCoreApplication.translate("MiSleep", u"Show all labeled markers; double-click to jump", None))
#endif // QT_CONFIG(tooltip)
        self.StartEndListBt.setText(QCoreApplication.translate("MiSleep", u"Start-End list", None))
#if QT_CONFIG(tooltip)
        self.StartEndListBt.setToolTip(QCoreApplication.translate("MiSleep", u"Show all start-end events; double-click to jump", None))
#endif // QT_CONFIG(tooltip)
        self.MarkerRadio.setText(QCoreApplication.translate("MiSleep", u"Marker", None))
        self.NREMBt.setText(QCoreApplication.translate("MiSleep", u"1:NREM", None))
        self.TimeDock.setWindowTitle(QCoreApplication.translate("MiSleep", u"Time", None))
        self.DateTimeEdit.setDisplayFormat(QCoreApplication.translate("MiSleep", u"dd - HH:mm:ss", None))
        self.ShowRangeCombo.setItemText(0, QCoreApplication.translate("MiSleep", u"Show 30 seconds", None))
        self.ShowRangeCombo.setItemText(1, QCoreApplication.translate("MiSleep", u"Show 1 minute", None))
        self.ShowRangeCombo.setItemText(2, QCoreApplication.translate("MiSleep", u"Show 5 minutes", None))
        self.ShowRangeCombo.setItemText(3, QCoreApplication.translate("MiSleep", u"Show 30 minutes", None))
        self.ShowRangeCombo.setItemText(4, QCoreApplication.translate("MiSleep", u"Show 1 hour", None))

        self.CustomSecondsCheck.setText(QCoreApplication.translate("MiSleep", u"Customize seconds", None))
        self.menuFile.setTitle(QCoreApplication.translate("MiSleep", u"File", None))
        self.menuTools.setTitle(QCoreApplication.translate("MiSleep", u"Tools", None))
        self.menuEvent_Detection.setTitle(QCoreApplication.translate("MiSleep", u"Event Detection", None))
        self.menuAuto_Stage.setTitle(QCoreApplication.translate("MiSleep", u"Auto Stage", None))
        self.menuResult.setTitle(QCoreApplication.translate("MiSleep", u"Result", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MiSleep", u"Help", None))
    # retranslateUi

