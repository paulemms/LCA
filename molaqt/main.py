import sys
import getopt
import logging
import webbrowser
from zipfile import ZipFile

from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import QMessageBox, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

import molaqt.qrc_resources
import molaqt.dbview as dbv
import molaqt.manager as mt
import molaqt.widgets as mw
import molaqt.utils as mu
from molaqt.console import QtConsoleWindow


class MolaMainWindow(QMainWindow):
    """
    Main window for the molaqt application. It defines the menus, toolbars and the main widget.
    """

    def __init__(self, argv):
        super(MolaMainWindow, self).__init__()

        # process arguments
        opts, args = getopt.getopt(argv, 'd', ['development'])
        dev = False
        for opt, arg in opts:
            if opt in ('-d', '--development'):
                dev = True

        # general configuration
        self.development = False
        self.system = mu.system_settings(development=dev)
        self.qt_console = None

        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle(self.system['app_name'])
        self.setWindowIcon(QIcon(":python-logo.png"))
        self.statusBar()

        # model configuration
        self.new_model_action = QAction(QIcon(":New.svg"), "&New ...", self)
        self.new_model_action.setShortcut("Ctrl+N")
        self.new_model_action.triggered.connect(self.new_model)
        self.save_model_action = QAction(QIcon(":Save.svg"), "&Save", self)
        self.save_model_action.setShortcut("Ctrl+S")
        self.save_model_action.triggered.connect(self.save_model)
        self.build_model_action = QAction(QIcon(":Build.svg"), "&Build", self)
        self.build_model_action.setShortcut("Ctrl+B")
        self.build_model_action.triggered.connect(self.build_model)
        self.run_model_action = QAction(QIcon(":Run.svg"), "&Run", self)
        self.run_model_action.setShortcut("Ctrl+R")
        self.run_model_action.triggered.connect(self.run_model)
        close_model_action = QAction("&Close", self)
        close_model_action.triggered.connect(self.close_model)
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Alt+E")
        exit_action.setStatusTip('Exit mola')
        exit_action.triggered.connect(self.close_application)

        # database
        import_sqlite_db_action = QAction("&Import sqlite ...", self)
        import_sqlite_db_action.setStatusTip('Import sqlite database')
        import_sqlite_db_action.triggered.connect(self.import_sqlite_database)
        self.open_db_action = QAction(QIcon(":Library.svg"), "&Open ...", self)
        self.open_db_action.setStatusTip('Open database')
        self.open_db_action.triggered.connect(self.open_database)

        # help
        general_specification_v5_action = QAction("&General Specification v5", self)
        general_specification_v5_action.triggered.connect(
            lambda: self.open_url(doc_file='General_Specification_v5.html'))
        github_home_action = QAction('&Github Home', self)
        github_home_action.triggered.connect(lambda: self.open_url(url='https://github.com/paulemms/LCA/wiki'))
        console_action = QAction("Qt Console", self)
        console_action.triggered.connect(self.console)
        self.about_action = QAction(QIcon(":Help.svg"), "&About", self)
        self.about_action.triggered.connect(self.about)

        # menus
        main_menu = self.menuBar()
        model_menu = main_menu.addMenu('&Model')
        model_menu.addAction(self.new_model_action)
        model_menu.addAction(self.save_model_action)
        model_menu.addAction(close_model_action)
        model_menu.addAction(exit_action)

        db_menu = main_menu.addMenu('&Database')
        db_menu.addAction(import_sqlite_db_action)
        db_menu.addAction(self.open_db_action)

        help_menu = main_menu.addMenu('&Help')
        help_menu.addAction(general_specification_v5_action)
        help_menu.addAction(github_home_action)
        help_menu.addAction(console_action)
        help_menu.addAction(self.about_action)

        self._create_toolbars()

        self.manager = mt.ModelManager(self.system)
        self.db_view = []
        self.setCentralWidget(self.manager)
        self.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def open_url(self, doc_file=None, url=None):
        if doc_file:
            url = self.system['system_doc_path'].joinpath(doc_file).resolve().as_uri()
        webbrowser.open(url, new=2)  # new tab

    def about(self):
        self.about_widget = mw.AboutWidget()

    def console(self):
        self.qt_console = QtConsoleWindow(self.manager)
        self.qt_console.show()

    def shutdown_kernel(self):
        if self.qt_console is not None:
            self.qt_console.shutdown_kernel()

    def close_application(self):
        choice = QMessageBox.question(self, 'Exit ' + self.system['app_name'], "Confirm exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def import_sqlite_database(self):
        zip_filter = 'zip files (*.zip)'
        # zip_name = QFileDialog.getOpenFileName(self, 'Import sqlite database', str(Path.home()), zip_filter)
        zip_name = QFileDialog.getOpenFileName(self, 'Import sqlite database', 'C:\data\openlca\zip', zip_filter)
        if zip_name[0] == '':
            return
        db_output_path = self.system['data_path'].joinpath(Path(zip_name[0]).with_suffix('.sqlite').name)
        if db_output_path.exists():
            QMessageBox.critical(self, 'Error', 'Database already exists', QMessageBox.Ok)
        else:
            try:
                logging.info('Uncompressing %s to %s' % (zip_name[0], self.system['data_path']))
                with ZipFile(zip_name[0], 'r') as zr:
                    zr.extractall(self.system['data_path'])
                self.manager.add_database(db_output_path)
            except Exception as e:
                QMessageBox.critical(self, 'Error', 'Cannot uncompress ' + zip_name[0],
                                     QMessageBox.Ok)

    def open_database(self):
        sqlite_filter = 'sqlite files (*.sqlite)'
        db_name = QFileDialog.getOpenFileName(self, 'Open database', str(self.system['data_path']),
                                              sqlite_filter)
        logging.INFO(db_name)
        if db_name[0] != '':
            db_view = dbv.DbView(db_name[0])
            self.db_view.append(db_view)
            db_view.show()
        else:
            logging.info('Cancelled open database')

    def new_model(self):
        config_file = self.manager.new_model()
        if config_file is not None:
            self.save_model()

    def save_model(self):
        config_file = self.manager.save_model()
        if config_file is not None:
            self.setWindowTitle(config_file.stem + ' - molaqt')
            self.statusBar().showMessage('Saved model to ' + str(config_file), 4000)

    def build_model(self):
        ok = self.manager.build_model()
        if ok:
            self.statusBar().showMessage('Built model', 4000)

    def run_model(self):
        ok = self.manager.run_model()
        if ok:
            self.statusBar().showMessage('Solved model', 4000)

    def close_model(self):
        is_closed = self.manager.close_model()
        if is_closed:
            self.setWindowTitle(self.system['app_name'])

    def _create_toolbars(self):
        main_tool_bar = self.addToolBar("Main")
        main_tool_bar.setIconSize(QSize(24, 24))
        main_tool_bar.addAction(self.new_model_action)
        main_tool_bar.addAction(self.save_model_action)
        main_tool_bar.addAction(self.open_db_action)
        main_tool_bar.addAction(self.about_action)

        model_tool_bar = self.addToolBar("Model")
        model_tool_bar.setIconSize(QSize(24, 24))
        model_tool_bar.addAction(self.build_model_action)
        model_tool_bar.addAction(self.run_model_action)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MolaMainWindow(sys.argv[1:])
    app.aboutToQuit.connect(gui.shutdown_kernel)
    sys.exit(app.exec_())
