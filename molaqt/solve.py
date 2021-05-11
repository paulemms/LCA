import io
import traceback

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QTextEdit, QLabel, QComboBox, QVBoxLayout
from PyQt5.QtCore import Qt
import pyomo.environ as pe

import molaqt.dialogs as mdg


class ModelSolve(QWidget):

    def __init__(self, lookup, controller=None):

        super().__init__()
        self._concrete_model = None
        self.results = None
        self.lookup = lookup
        self.controller = controller

        # button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_button_clicked)

        # objectives
        self.objective_combobox = QComboBox()
        self.objective_combobox.currentIndexChanged.connect(self.objective_changed)

        # solvers
        self.solver_combobox = QComboBox()
        self.solver_combobox.addItem('glpk')
        self.solver_combobox.currentIndexChanged.connect(self.solver_changed)

        # log output widget
        self.log = QTextEdit()

        # box for controls
        self.run_box = QVBoxLayout()
        self.run_box.setAlignment(Qt.AlignTop)
        self.run_box.addWidget(QLabel('Objective'), alignment=Qt.AlignTop)
        self.run_box.addWidget(self.objective_combobox, alignment=Qt.AlignTop)
        self.run_box.addWidget(QLabel('Solver'), alignment=Qt.AlignTop)
        self.run_box.addWidget(self.solver_combobox, alignment=Qt.AlignTop)
        self.run_box.addWidget(QLabel(''), alignment=Qt.AlignTop)
        self.run_box.addWidget(self.run_button, alignment=Qt.AlignTop)
        self.run_box.addStretch(0)

        # arrange widgets in grid
        grid_layout = QGridLayout()
        grid_layout.addLayout(self.run_box, 0, 0, 2, 1)
        grid_layout.addWidget(QLabel('Solver output'), 0, 1)
        grid_layout.addWidget(self.log, 1, 1)
        grid_layout.setColumnStretch(1, 2)
        self.setLayout(grid_layout)

    @property
    def concrete_model(self):
        return self._concrete_model

    @concrete_model.setter
    def concrete_model(self, model):
        print('Concrete model changed in ModelRun')
        self._concrete_model = model
        self.objectives = {}
        self.objective_combobox.clear()
        for i, obj in enumerate(model.component_objects(pe.Objective)):
            self.objective_combobox.addItem(obj.name)
            # activate first objective
            if i == 0:
                obj.activate()
            else:
                obj.deactivate()

    def objective_changed(self):
        for i, obj in enumerate(self._concrete_model.component_objects(pe.Objective)):
            if i == self.objective_combobox.currentIndex():
                obj.activate()
            else:
                obj.deactivate()

    def solver_changed(self):
        print('Solver changed')

    def run_button_clicked(self):
        print('Run button clicked')
        if self._concrete_model is not None:
            opt = pe.SolverFactory("glpk")

            try:
                self.results = opt.solve(self.concrete_model)
                output = io.StringIO()
                self.results.write(ostream=output)
                self.log.setText(output.getvalue())

                if self.controller.model_view_manager is not None:
                    self.controller.model_view_manager.concrete_model = self._concrete_model
                return True
            except Exception as e:
                self.dlg = mdg.critical_error_box("Uncaught exception for model run", str(e), traceback.format_exc())
                self.dlg.show()
        else:
            print("No successful build")
        return False

