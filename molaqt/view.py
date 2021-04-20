"""
Module to present Qt views of a concrete pyomo model from a Specification object
"""
import io

from PyQt5.QtWidgets import QWidget,  QTreeWidget, QTableView, QGridLayout, \
    QTreeWidgetItem, QLabel, QHeaderView, QCheckBox, QComboBox, QStackedWidget
import pyomo.environ as pe
import pandas as pd

import mola.output as mo
import molaqt.datamodel as md


class ModelViewManager(QWidget):
    """
    Qt widget to select the viewer object
    """

    def __init__(self, lookup):

        super().__init__()
        self._concrete_model = None
        self.results = None
        self.lookup = lookup

        # output viewers
        self.viewer = {'Tabular Viewer 1': TabularModelViewer(lookup), 'Tabular Viewer 2': TestModelViewer(lookup)}
        self.stacked_widget = QStackedWidget()
        for o in self.viewer.values():
            self.stacked_widget.addWidget(o)

        # viewer combobox
        self.viewer_combobox = QComboBox()
        self.viewer_combobox.addItems(self.viewer.keys())
        self.viewer_combobox.currentIndexChanged.connect(self.viewer_changed)

        # arrange widgets in grid
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.viewer_combobox, 0, 0)
        self.grid_layout.addWidget(self.stacked_widget, 1, 0)
        self.setLayout(self.grid_layout)

    @property
    def concrete_model(self):
        return self._concrete_model

    @concrete_model.setter
    def concrete_model(self, model):
        print('Concrete model changed in ModelViewManager')
        self._concrete_model = model
        # propagate model to viewers
        for view in self.viewer.values():
            view.concrete_model = model

    def viewer_changed(self, i):
        new_viewer_name = self.viewer_combobox.currentText()
        print('Viewer changed to', new_viewer_name)
        self.stacked_widget.setCurrentIndex(i)


class ModelViewer(QWidget):
    """
    ModelViewer interface
    """

    def __init__(self, lookup):

        super().__init__()
        self._concrete_model = None
        self.lookup = lookup

    @property
    def concrete_model(self):
        return self._concrete_model

    @concrete_model.setter
    def concrete_model(self, model):
        self._concrete_model = model


class TabularModelViewer(ModelViewer):
    """
    Qt widget to show a tabular view of a concrete model
    """

    def __init__(self, lookup):

        super().__init__(lookup)

        # checkboxes
        self.nonzero_checkbox = QCheckBox('Non-zero flows')
        self.nonzero_checkbox.toggle()
        self.nonzero_checkbox.clicked.connect(self.checkbox_clicked)
        self.distinct_levels_checkbox = QCheckBox('Distinct levels')
        self.distinct_levels_checkbox.toggle()
        self.distinct_levels_checkbox.clicked.connect(self.checkbox_clicked)

        # add list widget for output
        self.run_tree = QTreeWidget()
        self.run_tree.setHeaderLabels(['Component'])
        self.run_tree.itemClicked.connect(self.run_item_clicked)

        # add table for run content
        self.run_table = QTableView()
        self.run_table.setSelectionBehavior(QTableView.SelectRows)

        # component documentation
        self.cpt_doc = QLabel()

        # arrange widgets in grid
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Model'), 0, 0)
        grid_layout.addWidget(self.run_tree, 1, 0)
        grid_layout.addWidget(self.cpt_doc, 0, 1)
        grid_layout.addWidget(self.distinct_levels_checkbox, 0, 2)
        grid_layout.addWidget(self.nonzero_checkbox, 0, 3)
        grid_layout.addWidget(self.run_table, 1, 1, 2, 3)
        grid_layout.setColumnStretch(1, 2)
        self.setLayout(grid_layout)

    @ModelViewer.concrete_model.setter
    def concrete_model(self, model):
        print('Concrete model changed in TabularModelViewer')
        self._concrete_model = model
        self.run_tree.clear()
        self.run_table.setModel(md.PandasModel(pd.DataFrame()))
        var_item = QTreeWidgetItem(self.run_tree, ['Variables'])
        for var in self._concrete_model.component_objects(pe.Var, active=True):
            QTreeWidgetItem(var_item, [var.name])

        objective_item = QTreeWidgetItem(self.run_tree, ['Objective'])
        for obj in self._concrete_model.component_objects(pe.Objective):
            if obj.active:
                QTreeWidgetItem(objective_item, [obj.name])

        self.run_tree.expandAll()

    def viewer_changed(self):
        print('Viewer changed')

    def checkbox_clicked(self):
        if self.run_tree:
            item = self.run_tree.selectedItems()
            if item:
                self.run_item_clicked(item[0])

    def run_item_clicked(self, item):
        print('Run item', item.text(0), 'clicked')
        output = io.StringIO()
        if item.parent() is not None:
            if item.parent().text(0) == 'Variables':
                cpt = self._concrete_model.find_component(item.text(0))
                self.cpt_doc.setText(item.text(0) + ': ' + cpt.doc)
                df = mo.get_entity(cpt, self.lookup, units=True,
                                   non_zero=self.nonzero_checkbox.isChecked(),
                                   distinct_levels=self.distinct_levels_checkbox.isChecked()
                                   )
                run_model = md.PandasModel(df)
                self.run_table.setModel(run_model)
                self.run_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.run_table.resizeRowsToContents()
            elif item.parent().text(0) == 'Objective':
                cpt = self._concrete_model.find_component(item.text(0))
                self.cpt_doc.setText(cpt.doc)
                df = mo.get_entity(cpt, self.lookup, units=True)
                run_model = md.PandasModel(df)
                self.run_table.setModel(run_model)

        output.close()


class TestModelViewer(ModelViewer):
    """
    Qt widget to show a tabular view of a concrete model
    """

    def __init__(self, lookup):

        super().__init__(lookup)

        # checkboxes
        self.nonzero_checkbox = QCheckBox('Non-zero flows')
        self.nonzero_checkbox.toggle()
        self.nonzero_checkbox.clicked.connect(self.checkbox_clicked)
        self.distinct_levels_checkbox = QCheckBox('Distinct levels')
        self.distinct_levels_checkbox.toggle()
        self.distinct_levels_checkbox.clicked.connect(self.checkbox_clicked)

        # add list widget for output
        self.run_tree = QTreeWidget()
        self.run_tree.setHeaderLabels(['Component'])
        self.run_tree.itemClicked.connect(self.run_item_clicked)

        # add table for run content
        self.run_table = QTableView()
        self.run_table.setSelectionBehavior(QTableView.SelectRows)

        # component documentation
        self.cpt_doc = QLabel()

        # arrange widgets in grid
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Test'), 0, 0)
        grid_layout.addWidget(self.run_tree, 1, 0)
        grid_layout.addWidget(self.cpt_doc, 0, 1)
        grid_layout.addWidget(self.distinct_levels_checkbox, 0, 2)
        grid_layout.addWidget(self.nonzero_checkbox, 0, 3)
        grid_layout.addWidget(self.run_table, 1, 1, 2, 3)
        grid_layout.setColumnStretch(1, 2)
        self.setLayout(grid_layout)

    @ModelViewer.concrete_model.setter
    def concrete_model(self, model):
        print('Concrete model changed in TestModelViewer')
        self._concrete_model = model
        self.run_tree.clear()
        self.run_table.setModel(md.PandasModel(pd.DataFrame()))
        var_item = QTreeWidgetItem(self.run_tree, ['Variables'])
        for var in self._concrete_model.component_objects(pe.Var, active=True):
            QTreeWidgetItem(var_item, [var.name])

        objective_item = QTreeWidgetItem(self.run_tree, ['Objective'])
        for obj in self._concrete_model.component_objects(pe.Objective):
            if obj.active:
                QTreeWidgetItem(objective_item, [obj.name])

        self.run_tree.expandAll()

    def viewer_changed(self):
        print('Viewer changed')

    def checkbox_clicked(self):
        if self.run_tree:
            item = self.run_tree.selectedItems()
            if item:
                self.run_item_clicked(item[0])

    def run_item_clicked(self, item):
        print('Run item', item.text(0), 'clicked')
        output = io.StringIO()
        if item.parent() is not None:
            if item.parent().text(0) == 'Variables':
                cpt = self._concrete_model.find_component(item.text(0))
                self.cpt_doc.setText(item.text(0) + ': ' + cpt.doc)
                df = mo.get_entity(cpt, self.lookup, units=True,
                                   non_zero=self.nonzero_checkbox.isChecked(),
                                   distinct_levels=self.distinct_levels_checkbox.isChecked()
                                   )
                run_model = md.PandasModel(df)
                self.run_table.setModel(run_model)
                self.run_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.run_table.resizeRowsToContents()
            elif item.parent().text(0) == 'Objective':
                cpt = self._concrete_model.find_component(item.text(0))
                self.cpt_doc.setText(cpt.doc)
                df = mo.get_entity(cpt, self.lookup, units=True)
                run_model = md.PandasModel(df)
                self.run_table.setModel(run_model)

        output.close()
