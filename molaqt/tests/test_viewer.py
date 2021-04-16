# test of Viewer widget
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

import molaqt.viewer as mv
import molaqt.utils as mqu

app = QApplication(sys.argv)


class ModelViewerTest(TestCase):
    def test_model_viewer(self):

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

        # setup a model viewer
        model_viewer = mv.ModelViewer(lookup)
        model_viewer.concrete_model = instance

        model_viewer.resize(800, 600)
        model_viewer.show()

        # go through each variable and click on it
        model_viewer.run_tree.expandAll()
        variables = model_viewer.run_tree.topLevelItem(0)
        for c in range(variables.childCount()):
            v = variables.child(c)
            print(v.text(0))
            rect = model_viewer.run_tree.visualItemRect(v)
            QTest.mouseClick(model_viewer.run_tree.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())

        if 'IGNORE_EXEC' not in os.environ:
            app.exec()

        self.assertIsInstance(model_viewer, mv.ModelViewer)

