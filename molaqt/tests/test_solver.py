# test of Solver widget
import sys
import os
from unittest import TestCase

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt

import mola.dataimport as di
import mola.dataview as dv
import mola.build as mb

import molaqt.solver as ms
import molaqt.utils as mqu

app = QApplication(sys.argv)


class ModelSolverTest(TestCase):
    def test_model_solver(self):

        setting = mqu.system_settings(testing=True)
        config_path = setting['config_path'].joinpath('Lemon_Toy_Model.json')
        config = mb.get_config(config_path)
        instance = mb.build_instance(config)

        # get lookups from db
        conn = di.get_sqlite_connection()
        lookup = dv.LookupTables(conn)

        # setup a model run
        model_solver = ms.ModelSolver(lookup)
        model_solver.concrete_model = instance
        model_solver.resize(800, 600)
        model_solver.show()

        # run the model
        QTest.mouseClick(model_solver.run_button, Qt.LeftButton)

        if 'IGNORE_EXEC' not in os.environ:
            app.exec()

        self.assertIsInstance(model_solver, ms.ModelSolver)

