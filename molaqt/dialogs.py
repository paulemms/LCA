from pathlib import Path

from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QFileDialog
from PyQt5.QtWidgets import QComboBox, QMessageBox, QPushButton, QHBoxLayout, QWidget, QTextEdit

import mola.specification5 as ms
import molaqt.controllers as mqc


class NewModelDialog(QDialog):
    def __init__(self, parent=None, db_files=None):
        super().__init__(parent)
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
        self.specifications = {cls.name: cls for cls in ms.Specification.__subclasses__()}
        for spec in self.specifications:
            self.specification.addItem(spec)

        # documentation
        self.doc_widget = DocWidget()

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
        print("Specification changed to", spec_name[index])

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
        return (
            self.name.text(),
            current_spec_class,
            current_builder_class,
            current_db,
            self.doc_widget.path.text()
        )


class DocWidget(QWidget):

    def __init__(self):
        super().__init__()

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
        doc_file = QFileDialog.getOpenFileName(self, 'Open file', str(Path.home()),
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
    dlg = QMessageBox()
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.setDetailedText(detailed_text)
    details_box = dlg.findChild(QTextEdit)
    details_box.setFixedSize(600, 400)
    dlg.setIcon(QMessageBox.Critical)

    return dlg
