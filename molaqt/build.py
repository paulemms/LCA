import pandas as pd
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QTableView, QGridLayout, QMessageBox
import mola.output as mo
import mola.build as mb
import molaqt.datamodel as dm


class ModelBuild(QWidget):

    def __init__(self, controller):

        super().__init__()
        self.concrete_model = None
        self.controller = controller

        # button
        self.build_button = QPushButton("Build")
        self.build_button.clicked.connect(self.build_button_clicked)

        # add list widget for user-defined sets
        self.build_list = QListWidget()
        self.build_items = ['Sets', 'Parameters', 'Constraints', 'Objectives']
        self.build_list.itemClicked.connect(self.build_item_clicked)

        # add table for build content
        self.build_table = QTableView()
        self.build_table.setModel(dm.PandasModel(pd.DataFrame()))

        # arrange widgets in grid
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.build_button, 0, 0)
        grid_layout.addWidget(self.build_list, 1, 0)
        grid_layout.addWidget(self.build_table, 0, 1, 2, 1)
        grid_layout.setColumnStretch(1, 2)
        self.setLayout(grid_layout)

    def build_button_clicked(self):
        print('Build started')
        try:
            config = self.controller.get_config()
            self.concrete_model = mb.build_instance(config, self.controller.spec.settings)
            if self.controller.model_run is not None:
                self.controller.model_run.concrete_model = self.concrete_model
            self.build_list.clear()
            self.build_list.addItems(self.build_items)
            print('Build completed')
        except Exception as e:
            print(e)
            self.dialog_critical(str(e))

    def build_item_clicked(self, item):
        print('Build item', item.text(), 'clicked')
        if self.concrete_model is not None:
            if item.text() == 'Sets':
                df = mo.get_sets_frame(self.concrete_model)
            elif item.text() == 'Parameters':
                df = mo.get_parameters_frame(self.concrete_model)
            elif item.text() == 'Constraints':
                df = mo.get_constraints_frame(self.concrete_model)
            elif item.text() == 'Objectives':
                df = mo.get_objectives_frame(self.concrete_model)
            else:
                df = pd.DataFrame({'a': [1]})
            self.build_table.setModel(dm.PandasModel(df))
            self.build_table.resizeColumnsToContents()
            #self.build_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()


