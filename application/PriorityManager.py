#! /usr/bin/python
######################
# PriorityManager.py #
######################
import sys
import logging
from time import strftime
from PyQt5.QtWidgets import QApplication
from Model import Model
from MainController import MainController
from MainView import MainView

logging.basicConfig(filename=strftime(r'../log/%Y%m%d.log'), level=logging.DEBUG,
                    format='%(levelname)s: %(asctime)s.%(msecs)03d - %(name)s - %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('Main')
global_vars = dict(config_file='PriorityManager.conf')


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        log.debug('Start of program')
        self.model = Model(db_config=global_vars['config_file'])
        self.main_ctrl = MainController(self.model)
        self.main_view = MainView(self.model, self.main_ctrl)

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())
