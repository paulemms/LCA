# test of model viewer widgets
import sys
import os
from unittest import TestCase

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
import pyomo.environ as pe

import mola.dataimport as di
import mola.dataview as dv
import mola.build as mb

import molaqt.view as mv
import molaqt.utils as mqu

app = QApplication(sys.argv)

# load a model and solve it for viewing
setting = mqu.system_settings(testing=True)
config_path = setting['config_path'].joinpath('Lemon_Toy_Model.json')
config = mb.get_config(config_path)
instance = mb.build_instance(config)
for i, obj in enumerate(instance.component_objects(pe.Objective)):
    # activate first objective
    if i == 0:
        obj.activate()
    else:
        obj.deactivate()
opt = pe.SolverFactory("glpk")
opt.solve(instance)

# get lookups from db
conn = di.get_sqlite_connection()
lookup = dv.LookupTables(conn)


class ModelViewManagerTest(TestCase):
    def test_init(self):

        # setup a model viewer
        model_view_manager = mv.ModelViewManager(lookup)
        model_view_manager.concrete_model = instance

        model_view_manager.resize(800, 600)
        model_view_manager.show()

        if 'IGNORE_EXEC' not in os.environ:
            app.exec()

        self.assertIsInstance(model_view_manager, mv.ModelViewManager)


class TabularViewerTest(TestCase):
    def test_init(self):

        # setup a tabular model viewer
        tabular_view = mv.TabularModelViewer(lookup)
        tabular_view.concrete_model = instance

        tabular_view.resize(800, 600)
        tabular_view.show()

        # go through each variable and click on it
        tabular_view.run_tree.expandAll()
        variables = tabular_view.run_tree.topLevelItem(0)
        for c in range(variables.childCount()):
            v = variables.child(c)
            print(v.text(0))
            rect = tabular_view.run_tree.visualItemRect(v)
            QTest.mouseClick(tabular_view.run_tree.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())

        if 'IGNORE_EXEC' not in os.environ:
            app.exec()

        self.assertIsInstance(tabular_view, mv.TabularModelViewer)
