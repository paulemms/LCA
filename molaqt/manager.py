"""
Manage Mola models in Qt
"""
import logging
import re
import json
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QTreeWidget, QLabel, QTreeWidgetItem, QAction, \
    QMessageBox, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt
import molaqt.controllers as mc
import molaqt.dialogs as md
import molaqt.utils as mqu
from molaqt.console import QtConsoleWindow


class ModelManager(QWidget):
    """
    The main window for MolaQT. It manages optimisation models optionally using an openLCA database.
    """

    def __init__(self, system):
        super().__init__()
        self.system = system

        # model config file
        self.controller_config_file = None

        # workflow for building model
        self.controller = QLabel()

        # db tree
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderLabels(['Database'])
        self.db_tree.setMinimumWidth(250)
        self.db_tree.itemDoubleClicked.connect(self.load_model)

        # context menu for db tree
        self.db_tree.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.duplicate_model_action = QAction("Duplicate model")
        self.duplicate_model_action.triggered.connect(lambda: self.rename_model(copy=True))
        self.db_tree.addAction(self.duplicate_model_action)
        self.rename_model_action = QAction("Rename model")
        self.rename_model_action.triggered.connect(self.rename_model)
        self.db_tree.addAction(self.rename_model_action)
        self.delete_model_action = QAction("Delete model")
        self.delete_model_action.triggered.connect(self.delete_model)
        self.db_tree.addAction(self.delete_model_action)

        # model configurations that don't use a database
        self.no_db = QTreeWidgetItem(self.db_tree, ['None'])
        self.no_db.setExpanded(True)

        # find the user sqlite databases and add them to db_tree
        self.db_items = {}
        db_files = list(system['data_path'].glob('*.sqlite'))
        for db_file in db_files:
            self.db_items[db_file] = QTreeWidgetItem(self.db_tree, [db_file.stem])
            self.db_items[db_file].setExpanded(True)

        # add each model config to its database item by examining db_file entry
        config_item = []
        for cf in system['config_path'].glob('*.json'):
            with open(str(cf)) as fp:
                config_json = json.load(fp)
            if 'db_file' in config_json and config_json['db_file'] is not None:
                config_db = Path(config_json['db_file'])
                if config_db.exists():
                    config_item.append(QTreeWidgetItem(self.db_items[config_db], [cf.stem]))
            else:
                config_item.append(QTreeWidgetItem(self.no_db, [cf.stem]))

        # arrange widgets in splitter
        box = QHBoxLayout()
        self.splitter = QSplitter()
        self.splitter.addWidget(self.db_tree)
        self.splitter.addWidget(self.controller)
        self.splitter.setStretchFactor(1, 2)
        box.addWidget(self.splitter)

        self.setLayout(box)

    def load_model(self, item, col):
        if self.db_tree.indexOfTopLevelItem(item) == -1:
            config_file = self.system['config_path'].joinpath(item.text(0))
            logging.info('Loading model %s' % config_file)
            self.set_controller(config_file.with_suffix('.json'))

    def new_model(self):
        dialog = md.NewModelDialog(system=self.system, parent=self, db_files=self.db_items.keys())
        if dialog.exec():
            name, specification_class, controller_class, database, doc_file = dialog.get_inputs()
            config_file = self.system['config_path'].joinpath(name + '.json')
            if config_file.exists():
                QMessageBox.about(self, "Error", "Configuration file " + str(config_file.absolute()) +
                                  " already exists")
            else:
                if database:
                    item = QTreeWidgetItem(self.db_items[database], [config_file.stem])
                else:
                    item = QTreeWidgetItem(self.no_db, [config_file.stem])

                self.db_tree.clearSelection()
                item.setSelected(True)

                self.controller_config_file = config_file

                # get a new config dict
                new_config = mqu.get_new_config(specification_class, database, doc_file, controller_class)

                # instantiate controller using config
                new_controller = controller_class(new_config, self.system)

                # open new controller widget
                self.replace_controller(new_controller)

                return config_file

        return None

    def save_model(self):
        try:
            if self.is_model_loaded():
                config = self.controller.get_config()
                with open(str(self.controller_config_file), 'w') as fp:
                    json.dump(config, fp, indent=4)
                self.controller.saved = True

                logging.info('Saved model configuration to %s' % self.controller_config_file)

                return self.controller_config_file
            else:
                logging.info("Nothing to save")

        except Exception as e:
            md.critical_error_box('Critical error', str(e))

        return None

    def close_model(self):
        if self.controller_config_file is not None:
            choice = None
            if not self.controller.saved:
                choice = QMessageBox.question(self, 'Model not saved', "Confirm close?",
                                              QMessageBox.Yes | QMessageBox.No)

            if choice == QMessageBox.Yes or self.controller.saved:
                self.replace_controller(QLabel())
                logging.info('Closed model %s' % self.controller_config_file)
                return True

        return False

    def build_model(self):
        if self.is_model_loaded():
            # TODO: this requires the controller to have a model_build widget and button clicked method
            if hasattr(self.controller, 'model_build') and hasattr(self.controller.model_build, 'build_button_clicked'):
                ok = self.controller.model_build.build_button_clicked()
                return ok

    def run_model(self):
        if self.is_model_loaded():
            # TODO: this requires the controller to have a model_solve widget and button clicked method
            if hasattr(self.controller, 'model_solve') and hasattr(self.controller.model_solve, 'run_button_clicked'):
                ok = self.controller.model_solve.run_button_clicked()
                return ok

    def start_console(self):
        self.qt_console = QtConsoleWindow(manager=self)
        self.qt_console.show()

    def delete_model(self):
        index = self.db_tree.selectedItems()[0]
        if index.parent() is not None:
            db_index = index.parent()
            model_name = index.text(0)
            choice = QMessageBox.question(
                self,
                'Delete model',
                'Confirm delete ' + model_name + ' from ' + db_index.text(0) + '?',
                QMessageBox.Yes | QMessageBox.No
            )
            if choice == QMessageBox.Yes:
                db_index.removeChild(index)
                self.replace_controller(QLabel())
                self.system['config_path'].joinpath(model_name).with_suffix('.json').unlink()
                logging.info("Deleted %s" % model_name)
            else:
                pass

    def rename_model(self, copy=False):
        index = self.db_tree.selectedItems()[0]
        if index.parent() is not None:
            db_index = index.parent()
            model_name = index.text(0)
            dialog = md.RenameModelDialog(current_model_name=model_name, parent=self)
            if dialog.exec():
                old_config_path = self.system['config_path'].joinpath(model_name).with_suffix('.json')
                new_model_name = dialog.new_model_name.text()
                new_config_path = self.system['config_path'].joinpath(new_model_name).with_suffix('.json')
                if new_config_path.exists():
                    QMessageBox.about(self, "Error", "Configuration file " + str(new_config_path.absolute()) +
                                      " already exists")
                elif self.is_model_load() and not self.controller.saved:
                    QMessageBox.about(self, "Error", "Model not saved")
                else:
                    if self.controller is not None:
                        self.replace_controller(QLabel())
                    if copy:

                        new_config_path.write_text(old_config_path.read_text())
                    else:
                        db_index.removeChild(index)
                        old_config_path.rename(new_config_path)
                    qtw = QTreeWidgetItem(db_index, [new_model_name])
                    db_index.addChild(qtw)
                    self.db_tree.clearSelection()
                    qtw.setSelected(True)
                    logging.info('Renamed {} to {}'.format(model_name, dialog.new_model_name.text()))

    def set_controller(self, config_file):
        self.controller_config_file = config_file
        if self.parent() is not None:
            self.parent().setWindowTitle(config_file.stem + ' - molaqt')

        if not config_file.exists():
            logging.error("Cannot find configuration file %s" % config_file)
            return False

        # get configuration
        with open(config_file) as fp:
            user_config = json.load(fp)

        # instantiate controller using config if available otherwise default to StandardController
        if 'controller' in user_config:
            search = re.search("<class '(.*?)\.(.*?)\.(.*?)'>", user_config['controller'])
            class_name = search.group(3)
            class_ = getattr(mc, class_name)
            new_controller = class_(user_config, self.system)
        else:
            new_controller = mc.StandardController(user_config, self.system)

        self.replace_controller(new_controller)
        return True

    def replace_controller(self, new_controller):
        self.controller.deleteLater()  # ensures Qt webengine process gets shutdown
        self.splitter.replaceWidget(1, new_controller)
        self.splitter.update()
        self.splitter.setStretchFactor(1, 2)
        self.controller = new_controller

    def add_database(self, db_path):
        db_item = QTreeWidgetItem(self.db_tree, [db_path.stem])
        self.db_items[db_path] = db_item
        db_item.setSelected(True)

    def is_model_loaded(self):
        return not isinstance(self.controller, QLabel)

