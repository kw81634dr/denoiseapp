from PyQt5.QtWidgets import QFileDialog


def open_file() -> str:
    path = QFileDialog.getOpenFileName()[0]
    if path:
        print('path valid=', path)
        return path


class FileIO:
    pass
