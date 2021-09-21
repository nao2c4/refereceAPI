import sys
from PyQt5 import QtWidgets as QW
from PyQt5 import QtGui as QG
from utils import Reference, short, jjap_like
from typing import Union, Callable
import pyperclip
import re
from functools import partial


class DoiGUI(QW.QWidget):
    def __init__(self, parent: QW.QWidget = None) -> None:
        super(DoiGUI, self).__init__(parent)
        self.setFixedSize(1920, 1080)
        self.setWindowTitle('DOI Analyzer')

        self.ref = Reference()
        self.font = QG.QFont('Times New Roman', 16)

        self.output_widgets = []
        self.copy_buttons = []
        self.functions = []
        self._setup_widgets()

    def access_doi(self, url: str) -> None:
        ma = re.search(r'doi.org/(.+?$)', url)
        url = ma.group(1) if ma else url
        self.ref(url)
        [
            w.setText(f(self.ref))
            for w, f in zip(self.output_widgets, self.functions)
        ]
        return url

    def _setup_widgets(self) -> None:
        layout = QW.QVBoxLayout()
        layout.addLayout(self._setup_doi_widgets())
        layout.addLayout(self._setup_info_widgets(short))
        layout.addLayout(self._setup_info_widgets(jjap_like))
        layout.addLayout(
            self._setup_info_widgets(partial(jjap_like, initial=False))
        )
        self.setLayout(layout)

    def _setup_doi_widgets(self) -> Union[QW.QHBoxLayout, QW.QVBoxLayout]:
        self.doi_widget = QW.QLineEdit()
        self.doi_widget.setFont(self.font)
        self.doi_widget.textChanged.connect(self.access_doi)
        button = QW.QPushButton()
        button.setFont(self.font)
        button.setText('Paste')

        f = lambda x: self.doi_widget.setText(pyperclip.paste())
        button.clicked.connect(f)

        doi_layout = QW.QHBoxLayout()
        doi_layout.addWidget(self.doi_widget)
        doi_layout.addWidget(button)
        return doi_layout

    def _setup_info_widgets(self, fn: Callable[[Reference], str]):
        line_widget = QW.QTextEdit()
        line_widget.setFont(self.font)
        self.output_widgets.append(line_widget)
        button = QW.QPushButton()
        button.setText('Copy')
        button.setFont(self.font)
        self.functions.append(fn)

        f = lambda x: pyperclip.copy(line_widget.toPlainText())
        button.clicked.connect(f)

        layout = QW.QHBoxLayout()
        layout.addWidget(line_widget)
        layout.addWidget(button)
        return layout


if __name__ == '__main__':
    qapp = QW.QApplication([])
    app = DoiGUI()
    app.show()
    sys.exit(qapp.exec_())
