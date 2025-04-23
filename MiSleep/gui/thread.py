from PyQt5.QtCore import QObject, QThread
from misleep.gui.utils import second2time
from misleep.utils.annotation import lst2group
from misleep.io.signal_io import load_mat, write_edf, write_mat
import datetime

class SaveThread(QThread):

    def __init__(self, parent=None, file=None, file_path=None):
        """Save file to file path

        Parameters
        ----------
        parent : optional
        file : ANY, optional
            Any kinds of file to save, by default None
        file_path : str, optional
            File path for saving, by default None
        """
        super().__init__(parent)
        self.file = file
        self.file_path = file_path

    def save_config(self):
        """Configuration save function"""
        with open(self.file_path, 'w') as config_file:
            self.file.write(config_file)
    
    def save_anno(self):
        """Annotation save function, anno is an instance of MiAnnotation"""

        mianno, midata = self.file

        ac_time = datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S")
        marker = [', '.join([
            second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), '1',
            second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), '0', 
            '1', each[1]
        ]) for each in mianno.marker]

        start_end_label = [', '.join([
            second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), '1',
            second2time(round(each[1], 3), ac_time=ac_time, ms=True), str(round(each[1], 3)), '0', 
            '1', each[2]
        ]) for each in mianno.start_end]

        sleep_state = lst2group([[idx, each] 
                                 for idx, each in enumerate(mianno.sleep_state)])
        sleep_state = [', '.join([
            second2time(each[0], ac_time=ac_time), str(each[0]), '1',
            second2time(each[1], ac_time=ac_time), str(each[1]),
            '0', str(each[2]), mianno.state_map[each[2]]
        ]) for each in sleep_state]

        if len(marker) > 0:
            marker = [''] + marker
        if len(start_end_label) > 0:
            start_end_label = [''] + start_end_label

        annos = [
            "READ ONLY! DO NOT EDIT!\n4-INIT 3-Wake 2-REM 1-NREM",
            "Save time: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            "Acquisition time: " + ac_time.strftime("%Y-%m-%d %H:%M:%S"),
            "==========Marker==========" + '\n'.join(marker),
            "==========Start-End==========" + '\n'.join(start_end_label),
            "==========Sleep stage==========", '\n'.join(sleep_state)
        ]

        with open(self.file_path, 'w') as f:
            f.write('\n'.join(annos))
        return True
    
    def save_data(self):
        """Data save function"""
        midata= self.file
        if midata is None:
            return False

        if self.file_path.endswith('.mat'):
            write_mat(midata.signals, midata.channels, midata.sf, midata.time, self.file_path)
        elif self.file_path.endswith('.edf'):
            write_edf(midata.signals, midata.channels, midata.sf, midata.time, self.file_path)
        else:
            raise ValueError("File type not supported!")
        return True

class LoadThread(QThread):

    def __init__(self, parent=None, file_path=None):
        """Load data

        Parameters
        ----------
        parent : optional
        file_path : str, optional
            File path to load 
        """
        super().__init__(parent)
        self.file_path = file_path

    def load_mat_data(self):
        """Load data from a.mat file"""
        return load_mat(data_path=self.file_path)


