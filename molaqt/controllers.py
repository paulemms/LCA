from pathlib import Path
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout

import mola.dataimport as di
import mola.dataview as dv
import mola.build as mb
import mola.utils as mu
import molaqt.build as mqb
import molaqt.solve as ms
import molaqt.view as mv
import molaqt.widgets as mw


class Controller(QWidget):
    """
    A Controller is a collection of widgets with which to construct an optimisation problem from a specification.
    Implementations are derived from this class.
    """

    def __init__(self, user_config, system):
        super().__init__()
        self.user_config = user_config
        self.system = system

        self.saved = False
        self.spec = mb.create_specification(user_config['specification'], user_config['settings'])

        # merge user sets and parameters into spec defaults
        self.sets = self.spec.get_default_sets()
        self.sets.update(user_config['sets'])
        self.indexed_sets = self.spec.get_default_indexed_sets(self.sets)
        if 'indexed_sets' in user_config:
            self.indexed_sets.update(user_config['indexed_sets'])
        self.parameters = self.spec.get_default_parameters(self.sets, self.indexed_sets)
        self.parameters.update(user_config['parameters'])

        # if we need a db get lookups
        lookup_sets = [n for n, d in self.spec.user_defined_sets.items() if 'lookup' in d and d['lookup']]
        if len(lookup_sets) > 0 and 'db_file' in user_config:
            self.db_file = user_config['db_file']

            # instantiate db connection from config
            self.conn = di.get_sqlite_connection(self.db_file)

            # get lookups from db
            self.lookup = dv.LookupTables(self.conn)
        else:
            self.db_file = None
            self.lookup = dict()

    def get_config(self):
        """
        Create dict for model configuration file representing current model state
        :return: dict
        """
        self.update_state()
        config = {
            'settings': self.spec.settings,
            'doc_name': self.user_config['doc_name'],
            'specification': str(self.spec.__class__),
            'controller': self.user_config['controller'],
            'db_file': self.db_file,
            'sets': self.sets,
            'indexed_sets': self.indexed_sets,
            'parameters': self.parameters,
        }

        return config

    def update_state(self):
        """ Each controller must implement this method to update its state from memory """
        pass


class CustomController(Controller):

    def __init__(self, user_config, system):

        super().__init__(user_config, system)

        # add widgets for objective, network, build, run
        self.obj = mw.ObjectiveWidget(self.lookup, self.sets['KPI'])
        self.process_flow = mw.ProcessFlow(self.sets, self.parameters,
                                           self.spec, self.lookup, self.conn)
        p = {k: v for k, v in self.parameters.items() if k != 'J'}
        self.parameters_editor = mw.ParametersEditor(self.sets, p, self.spec, self.lookup)
        self.model_build = mqb.ModelBuild(self)
        self.model_solve = ms.ModelSolve(self.lookup, controller=self)
        self.model_view_manager = mv.ModelViewManager(self.lookup, self.spec)

        # initialize tab screen
        self.tabs = QTabWidget()

        # documentation tab for specification
        self.documentation = None
        if 'doc_name' in user_config and user_config['doc_name'] != '':
            doc_path = self.system['doc_path'].joinpath(user_config['doc_name'])
            if doc_path.exists():
                self.documentation = mw.DocWidget(doc_path)

        # Add tabs
        self.tabs.addTab(self.documentation, "Documentation")
        self.tabs.addTab(self.obj, "Objective")
        self.tabs.addTab(self.process_flow, "Processes and Flows")
        self.tabs.addTab(self.parameters_editor, "Parameters")
        self.tabs.addTab(self.model_build, "Build")
        self.tabs.addTab(self.model_solve, "Solve")
        self.tabs.addTab(self.model_view_manager, "View")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_state(self):
        self.parameters = mu.get_index_value(self.parameters_editor.par)
        # TODO: only allow process_flow to alter J
        p = self.process_flow.get_parameters()
        self.parameters.update({'J': p['J']})


class StandardController(Controller):

    def __init__(self, user_config, system):

        super().__init__(user_config, system)

        # add widgets for sets, parameters, build, run
        self.sets_editor = mw.SetsEditor(self.sets, self.spec, self.lookup)
        if hasattr(self.spec, 'user_defined_indexed_sets'):
            self.indexed_sets_editor = mw.IndexedSetsEditor(self.indexed_sets, self.sets, self.spec, self.lookup)
            self.parameters_editor = mw.ParametersEditor(self.sets, self.parameters,
                                                         self.spec, self.lookup,
                                                         self.indexed_sets_editor.get_indexed_sets)
        else:
            self.parameters_editor = mw.ParametersEditor(self.sets, self.parameters,
                                                         self.spec, self.lookup)

        self.model_build = mqb.ModelBuild(self)
        self.model_solve = ms.ModelSolve(self.lookup, controller=self)
        self.model_view_manager = mv.ModelViewManager(self.lookup, self.spec)

        # initialize tab screen
        self.tabs = QTabWidget()

        # documentation tab for specification
        self.documentation = None
        if 'doc_name' in user_config and user_config['doc_name'] != '':
            doc_path = self.system['doc_path'].joinpath(user_config['doc_name'])
            if doc_path.exists():
                self.documentation = mw.DocWidget(doc_path)

        # high-level configuration
        self.configure = None
        if self.spec.default_settings:
            self.configure = mw.ConfigurationWidget(self.spec)

        # Add tabs
        self.tabs.addTab(self.documentation, "Documentation")
        self.tabs.addTab(self.configure, "Configure")
        self.tabs.addTab(self.sets_editor, "Sets")
        if hasattr(self.spec, 'user_defined_indexed_sets'):
            self.tabs.addTab(self.indexed_sets_editor, "Indexed Sets")
        self.tabs.addTab(self.parameters_editor, "Parameters")
        self.tabs.addTab(self.model_build, "Build")
        self.tabs.addTab(self.model_solve, "Solve")
        self.tabs.addTab(self.model_view_manager, "View")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_state(self):
        self.parameters = mu.get_index_value(self.parameters_editor.par)
        if hasattr(self.spec, 'user_defined_indexed_sets'):
            self.indexed_sets = self.indexed_sets_editor.get_indexed_sets()

