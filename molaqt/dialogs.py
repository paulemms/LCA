"""
A collection of Qt Dialogs for MolaQT
"""
import logging
from pathlib import Path

from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QFileDialog
from PyQt5.QtWidgets import QComboBox, QMessageBox, QPushButton, QHBoxLayout, QWidget, QTextEdit

import mola.specification5 as ms
import molaqt.controllers as mqc


class NewModelDialog(QDialog):
    def __init__(self, system, parent=None, db_files=None):
        super().__init__(parent)
        self.system = system
        self.setWindowTitle("New Model")

        self.name = QLineEdit(self)
        self.name.setText('test_model')

        # builder combobox
        self.builder = QComboBox(self)
        self.builders = None
        self.builder_class = {
            "StandardController": mqc.StandardController,
            "CustomController": mqc.CustomController}

        # databases combobox
        self.database = QComboBox(self)
        self.db_files = {f.stem: f for f in db_files}
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        # specification combobox
        self.specification = QComboBox(self)
        self.specification.currentIndexChanged.connect(self.specification_changed)
        self.specifications = {cls.name: cls for cls in ms.Specification.__subclasses__()
                               if 'no_db_required' in cls.__dict__ or len(db_files) > 0}
        for spec in self.specifications:
            self.specification.addItem(spec)

        # documentation
        self.doc_widget = DocWidget(self.system)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Specification", self.specification)
        layout.addRow("Controller", self.builder)
        layout.addRow("Database", self.database)
        layout.addRow("Documentation", self.doc_widget)
        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def specification_changed(self, index):
        spec_name = list(self.specifications.keys())
        spec_class = list(self.specifications.values())
        logging.info("Specification changed to %s" % spec_name[index])

        # populate builder dropdown
        self.builder.clear()
        self.builders = spec_class[index].controllers
        for builder in self.builders:
            self.builder.addItem(builder)

        # populate database dropdown
        self.database.clear()
        if 'no_db_required' in spec_class[index].__dict__:
            self.database.addItem('None')
        else:
            self.database.addItems(self.db_files.keys())

    def get_inputs(self):
        spec_class = list(self.specifications.values())
        builder_text = list(self.builders.values())
        current_spec_class = spec_class[self.specification.currentIndex()]
        current_builder_class = self.builder_class[builder_text[self.builder.currentIndex()]]
        current_db = None if self.database.currentText() == 'None' else self.db_files[self.database.currentText()]
        doc_path = self.doc_widget.path.text()
        # if the file is in the doc_path store it as a relative file name
        if Path(doc_path).parent.resolve() == self.system['doc_path'].resolve():
            doc_path = Path(doc_path).name

        return (
            self.name.text(),
            current_spec_class,
            current_builder_class,
            current_db,
            doc_path
        )


class DocWidget(QWidget):

    def __init__(self, system):
        super().__init__()
        self.system = system

        # widgets
        self.path = QLineEdit()
        button = QPushButton('...')
        button.clicked.connect(self.find_file)

        # layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.path)
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def find_file(self):
        doc_file = QFileDialog.getOpenFileName(self, 'Open file', str(self.system['doc_path']),
                                               "HTML files (*.html)")
        if doc_file[0] != '':
            self.path.setText(doc_file[0])


class RenameModelDialog(QDialog):

    def __init__(self, current_model_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Model " + current_model_name)

        self.new_model_name = QLineEdit(self)
        self.new_model_name.setText(current_model_name)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("New model name", self.new_model_name)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)


def critical_error_box(title, text, detailed_text=None):
    logging.info('Error %s %s %s' % (title, text, detailed_text))
    dlg = QMessageBox()
    dlg.setWindowTitle(title)
    dlg.setText(text)
    if detailed_text:
        dlg.setDetailedText(detailed_text)
        details_box = dlg.findChild(QTextEdit)
        details_box.setFixedSize(600, 400)
    dlg.setIcon(QMessageBox.Critical)

    return dlg
