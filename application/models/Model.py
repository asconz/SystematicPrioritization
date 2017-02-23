#! /usr/bin/python
###################
# models\Model.py #
###################
import logging
from PyQt5.QtCore import QDate
from DB import PriorityModel, DetailModel, DBInterface
from ConfigParser import ParseConfig
log = logging.getLogger('model')


class Model(object):
    """ Contains data variables and logic to announce when updated by controller.
            Model.announce_update calls registered functions to refresh view (e.g.MainView.update_ui_from_model). """
    def __init__(self, db_config):
        self.db = db_connect(db_config)
        self.db.call_process(QDate.currentDate().toString("yyyy-MM-dd"))
        self._update_funcs, self._refresh_detail_funcs = [], []
        self.category_dict, self.status_dict = {}, {}
        self.get_cat_dict(), self.get_status_dict()

        #### model variable defaults/placeholders ####
        self.task_input = None
        self.weight_calc = '-'
        self.importance_input = None
        self.urgency_input = None
        self.difficulty_input = None
        self.i_slider = None
        self.u_slider = None
        self.d_slider = None
        self.cat_dropdown_index = self.category_dict.get('Misc', None)
        self.descr_input = ''
        self.date_due = None

        self.selected_row_index = -1
        self.perspective = 'Active'
        self.category_filter = None
        self.detail_filter = -1
        self.update_id = None
        self.status = None

        #### create Qt models for compatible widget types ####
        self.priority_model = PriorityModel(self.perspective, self.category_filter)
        self.detail_model = DetailModel(self.detail_filter)

    #####################
    def subscribe_update_func(self, func):
        """ To specify MainView widget-refresh """
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    def announce_update(self):
        self.priority_model = PriorityModel(self.perspective, self.category_filter)
        for func in self._update_funcs:
            func()

    #####################
    def subscribe_refresh_detail_filter(self, func):
        """ Refresh TableView on filter-choice """
        if func not in self._refresh_detail_funcs:
            self._refresh_detail_funcs.append(func)

    def announce_detail_refresh(self):
        for func in self._refresh_detail_funcs:
            func()

    def refresh_detail_filter(self):
        log.debug("refresh_detail_filter(): %s" % self.detail_filter)
        self.detail_model = DetailModel(self.detail_filter)
        self.announce_detail_refresh()

    #####################
    def priority_submit(self):
        if not self.update_id:
            self.priority_model.add_priority(
                self.task_input, self.weight_calc, self.cat_dropdown_index, self.descr_input,
                self.importance_input, self.urgency_input, self.difficulty_input, self.date_due)
        else:
            # if self.perspective == 'Overdue' and self.date_due >= QDate.currentDate():
            #    # consider updating status_id for overdue when new date_due is beyond curdate
            self.priority_model.update_priority(
                self.task_input, self.weight_calc, self.cat_dropdown_index, self.descr_input,
                self.importance_input, self.urgency_input, self.difficulty_input, self.date_due, self.update_id)
        self.status = self.priority_model.status
        self.detail_filter = -1
        self.update_id = None

    def db_priority_action(self, priority_id, action):
        """ Delete/Archive/Complete Priority """
        self.priority_model.priority_action(priority_id, action)
        self.status = self.priority_model.status
        # todo - set detail_filter = priority_id (except on delete)
        # todo (contd) - will need to account for perspective/category filters
        self.detail_filter = -1
        self.update_id = None

    #####################
    def get_cat_dict(self):
        """ pull category key, value pairs from db """
        for name, category_id in self.db.sql_query('SELECT CATEGORY, CATEGORY_ID FROM category'):
            self.category_dict[name] = category_id
        log.debug("Category Dict: %s" % self.category_dict)

    def get_status_dict(self):
        """ pull status key, value pairs from db """
        for name, status_id in self.db.sql_query('SELECT STATUS, STATUS_ID FROM status'):
            self.status_dict[name] = status_id
        log.debug("Status Dict: %s" % self.status_dict)


#####################
def db_connect(db_config):
    """ parse config and password files to connect to db """
    db_args = ParseConfig(db_config).db_args()

    with open(r'models/%s' % db_args['password'], 'r') as p_file:
        db_args['pw'] = p_file.read()

    return DBInterface(db_args)
