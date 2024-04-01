from PyQt5.QtCore import QObject, QThread


class SaveThread(QThread):

    def __init__(self, parent=None, file=None, file_path=None, file_type=None):
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
        self.file_type = file_type

        if self.file_type == 'config':
            self.save_config()

    def save_config(self):
        """Configuration save function"""
        with open(self.file_path, 'w') as config_file:
            self.file.write(config_file)