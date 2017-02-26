#! /usr/bin/python
###########################
# ctrls\MainController.py #
###########################
import logging
from Dialogs import Dialogs
log = logging.getLogger('main_ctrl')


class MainController(object):
    """ MainController `event` methods - called from MainView - contain control logic:
            Calculate new values, pass to Model, and announce to refresh MainView. """
    def __init__(self, model):
        log.debug('main_ctrl init')
        self.model = model
        self.dialog = Dialogs()
        self.task_name = 'Priority Detail'
        self.status, self.category_msg, self.row_msg = None, None, None

    #### MainView-signal control logic ####
    """## input_dialog ##"""
    def change_input_value(self, sender_name, text):
        if sender_name == 'task_input':
            self.model.task_input = text
        elif sender_name == 'descr_input':
            self.model.descr_input = text
        elif sender_name == 'category_dropdown':
            self.model.cat_dropdown_index = self.model.category_dict.get(text, None)

    def change_weight_metrics(self, importance, urgency, difficulty):
        self.model.importance_input = importance
        self.model.i_slider = importance
        self.model.urgency_input = urgency
        self.model.u_slider = urgency
        self.model.difficulty_input = difficulty
        self.model.d_slider = difficulty

    def calculate_weight(self):
        importance, urgency, difficulty = self.model.i_slider, self.model.u_slider, self.model.d_slider
        weighted_priority = importance * (10 - difficulty) * urgency / 5
        self.model.weight_calc = weighted_priority
        self.model.announce_update()

    def due_date_change(self, date):
        self.model.date_due = date

    def clear_due_date(self):
        self.model.date_due = None
        self.model.announce_update()

    def click_clear_btn(self):
        self.model.task_input = ''
        self.model.weight_calc = '-'
        self.model.importance_input = '0-10'
        self.model.urgency_input = '0-10'
        self.model.difficulty_input = '0-10'
        self.model.cat_dropdown_index = self.model.category_dict.get('Misc', None)
        self.model.descr_input = ''
        self.model.date_due = None
        self.model.update_id = None
        self.task_name = 'Priority Detail'
        self.model.refresh_detail_filter()
        self.model.announce_update()

    def click_submit_btn(self):
        self.model.priority_submit()
        self.status = self.model.status
        self.model.announce_update()

    """## MainWindow ##"""
    def change_perspective_filter(self, p_filter):
        self.model.perspective = p_filter
        self.model.announce_update()

    def change_category_filter(self, c_filter):
        self.model.category_filter = c_filter
        self.model.announce_update()

    def detail_id_check_new_filter(self):
        row_count = self.model.priority_model.rowCount()
        log.debug("%s records in view" % self.model.priority_model.rowCount())
        if not self.model.detail_filter == -1:
            for row in range(row_count):
                if self.model.priority_model.record(row).value('PRIORITY_ID') == self.model.detail_filter:
                    log.debug("Priority detail is row %s in new view." % row)
                    self.model.selected_row_index = row
                    return True
        else:
            return False

    def change_row_selection(self, index):
        log.debug("detail-filter pre refresh: %s" % self.model.detail_filter)
        if index.isValid():
            row_index = index.row()
            self.model.selected_row_index = row_index
            record = self.model.priority_model.record(row_index)
            task_id, self.task_name = int(record.value("PRIORITY_ID")), record.value("TASK")
            self.model.detail_filter = task_id
            self.row_msg = "Row %s \t\t\t ID %s \t\t-\t\t %s" % (row_index + 1, task_id, self.task_name)
        else:
            self.model.detail_filter = -1
            self.task_name = 'Priority Detail'
        self.model.refresh_detail_filter()
        self.status_msg()

    def click_edit_priority_btn(self, record):
        """ send record values to model for input group box"""
        self.model.task_input = record.value('TASK')
        self.model.descr_input = record.value('DESCRIPTION')
        self.change_weight_metrics(record.value('IMPORTANCE'), record.value('URGENCY'), record.value('DIFFICULTY'))
        self.model.cat_dropdown_index = self.model.category_dict.get(record.value('CATEGORY'), None)
        self.model.date_due = record.value('DATE_DUE').toString('yyyy-MM-dd')
        log.debug("Edit Priority -- existing date_due: %s" % self.model.date_due)
        self.model.update_id = int(record.value('PRIORITY_ID'))
        self.model.announce_update()

    def send_db_action(self, row_index, action):
        record = self.model.priority_model.record(row_index)
        priority_id, task = record.value('PRIORITY_ID'), record.value('TASK')
        if not self.dialog.question_box(action, task):
            self.status = "%s Canceled  -  '%s'" % (action, task)
        else:
            self.model.db_priority_action(priority_id, action)
            self.status = self.model.status
        self.model.announce_update()

    # current work to combine db_action buttons - 02-09
    # def send_db_action(self, row_index, action):
    #     record = self.model.priority_model.record(row_index)
    #     priority_id, task = record.value('PRIORITY_ID'), record.value('TASK')
    #     if action == 'Edit':
    #         self.model.update_id = priority_id
    #         self.populate_edit_dialog(record)
    #     elif self.dialog.question_box(action, task):
    #         self.model.db_priority_action(priority_id, action)
    #         self.status = self.model.status
    #     else:
    #         self.status = "%s Canceled  -  '%s'" % (action, task)
    #     self.model.announce_update()
    #
    # def populate_edit_dialog(self, record):
    #     """ send record values to model for input group box"""
    #     self.model.task_input = record.value('TASK')
    #     self.model.descr_input = record.value('DESCRIPTION')
    #     self.change_weight_metrics(record.value('IMPORTANCE'), record.value('URGENCY'), record.value('DIFFICULTY'))
    #     self.model.cat_dropdown_index = self.model.category_dict.get(record.value('CATEGORY'), None)
    #     self.model.date_due = record.value('DATE_DUE').toString('yyyy-MM-dd')
    #     # self.model.announce_update()

    def status_msg(self):
        if self.category_msg:
            self.status = self.category_msg + self.row_msg
        else:
            self.status = self.row_msg

    def schedule_task(self):  # Consider re: scheduling reminders
        """
        # Start an infinite loop that checks email and carries out instructions.

        log.debug('Email bot started. Press Ctrl-C to quit.')
        logging.debug('Email bot started.')
        while True:
            try:
                logging.debug('Getting instructions from email...')
                instructions = getInstructionEmails()
                for instruction in instructions:
                    logging.debug('Doing instruction: ' + instruction)
                    parseInstructionEmail(instruction)
            except Exception as err:
                logging.error(traceback.format_exc())

            # Wait 15 minutes before checking again
            logging.debug('Done processing instructions. Pausing for 15 minutes.')
            time.sleep(60 * 15)
        """
        pass
