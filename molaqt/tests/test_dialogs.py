# test dialog widgets
import os
import sys
from unittest import TestCase

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

import molaqt.dialogs as md
import molaqt.utils as mqu

app = QApplication(sys.argv)
system = mqu.system_settings(testing=True)


class Test(TestCase):
    def test_new_model_dialog(self):
        dialog = md.NewModelDialog(system=system, db_files=[])

        # change to a spec where we don't need a db so that 'OK' works
        index = dialog.specification.findText('AIMMS Example Specification', Qt.MatchFixedString)
        dialog.specification.setCurrentIndex(index)

        if 'IGNORE_EXEC' not in os.environ:
            if dialog.exec():
                print(dialog.get_inputs())

    # def test_doc_widget(self):
    #     self.fail()
    #
    # def test_rename_model_dialog(self):
    #     self.fail()
