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

import molaqt.solve as ms
import molaqt.utils as mqu

app = QApplication(sys.argv)


class ModelSolveTest(TestCase):
    def test_model_solve(self):

        setting = mqu.system_settings(testing=True)
        config_path = setting['config_path'].joinpath('Lemon_Toy_Model.json')
        config = mb.get_config(config_path)
        instance = mb.build_instance(config)

        # get lookups from db
        conn = di.get_sqlite_connection()
        lookup = dv.LookupTables(conn)

        # setup a model run
        model_solve = ms.ModelSolve(lookup)
        model_solve.concrete_model = instance
        model_solve.resize(800, 600)
        model_solve.show()

        # run the model
        QTest.mouseClick(model_solve.run_button, Qt.LeftButton)

        if 'IGNORE_EXEC' not in os.environ:
            app.exec()

        self.assertIsInstance(model_solve, ms.ModelSolve)

