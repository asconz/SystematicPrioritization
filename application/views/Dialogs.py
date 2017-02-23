#! /usr/bin/python
####################
# views\Dialogs.py #
####################
import sys
import logging
from PyQt5.QtCore import Qt, QSize, pyqtProperty, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QSlider, QDialog, QComboBox, QGridLayout, QLabel, QMessageBox,
                             QToolButton, QLineEdit, QDateEdit, QPushButton, QSizePolicy, QCalendarWidget)
log = logging.getLogger('views.Dialogs')


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)
        self.resize(850, 200)

        self.input_font = QFont()
        self.input_font.setBold(True)
        self.input_font.setWeight(75)

        self.label_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_size_policy.setHorizontalStretch(0)
        self.label_size_policy.setVerticalStretch(0)

        self.td_input_size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.td_input_size_policy.setHorizontalStretch(0)
        self.td_input_size_policy.setVerticalStretch(0)

        self.calc_input_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.calc_input_size_policy.setHorizontalStretch(0)
        self.calc_input_size_policy.setVerticalStretch(0)

        self.slider_size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.slider_size_policy.setHorizontalStretch(0)
        self.slider_size_policy.setVerticalStretch(0)

        self.category_dropdown = QComboBox()
        self.category_dropdown.setObjectName('category_dropdown')
        self.category_dropdown.addItem("Misc")
        self.category_dropdown.addItem("Career")
        self.category_dropdown.addItem("Finance")
        self.category_dropdown.addItem("Projects")

        self.task_input = QLineEdit()
        self.task_input.setObjectName('task_input')
        self.descr_input = QLineEdit()
        self.descr_input.setObjectName('descr_input')

        for td_input in [self.task_input, self.descr_input]:
            td_input.setSizePolicy(self.td_input_size_policy)

        self.task_label = QLabel('Task')
        self.category_label = QLabel('Category')
        self.descr_label = QLabel('Description')

        for tcd_label in [self.task_label, self.category_label, self.descr_label]:
            tcd_label.setSizePolicy(self.label_size_policy)
            tcd_label.setAlignment(Qt.AlignLeft)

        self.weight_label = QLabel('Priority Weighting')
        self.importance_label = QLabel('Importance')
        self.urgency_label = QLabel('Urgency')
        self.difficulty_label = QLabel('Difficulty')

        for calc_label in [self.weight_label, self.importance_label, self.urgency_label, self.difficulty_label]:
            calc_label.setSizePolicy(self.label_size_policy)
            calc_label.setAlignment(Qt.AlignCenter)

        self.weight_calc = QLabel('-')
        self.importance_input = QLabel('0-10')
        self.urgency_input = QLabel('0-10')
        self.difficulty_input = QLabel('0-10')

        for calc_input in [self.weight_calc, self.importance_input, self.urgency_input, self.difficulty_input]:
            calc_input.setSizePolicy(self.calc_input_size_policy)
            calc_input.setFont(self.input_font)
            calc_input.setAlignment(Qt.AlignCenter)

        self.i_slider = QSlider()
        self.u_slider = QSlider()
        self.d_slider = QSlider()

        for slider in [self.i_slider, self.u_slider, self.d_slider]:
            slider.setSizePolicy(self.slider_size_policy)
            slider.setMaximum(10)
            slider.setPageStep(1)
            slider.setProperty("value", 5)
            slider.setOrientation(Qt.Horizontal)
            slider.setTickPosition(QSlider.TicksBelow)

        self.calendar_icon = QIcon()
        self.calendar_icon.addPixmap(QPixmap(":/Schedule1.png"), QIcon.Normal, QIcon.Off)

        self.calendar_btn = QToolButton()
        self.calendar_btn.setText("Due-Date")
        self.calendar_btn.setIcon(self.calendar_icon)
        self.calendar_btn.setIconSize(QSize(30, 30))
        self.calendar_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.calendar_btn.setCheckable(True)
        self.calendar_btn.setToolTip("Assign/remove due-date")

        self.calendar_widget = PyDateEdit()
        self.calendar_widget.setHidden(True)

        self.dialog_btn_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.dialog_btn_size_policy.setHorizontalStretch(0)
        self.dialog_btn_size_policy.setVerticalStretch(0)

        self.clear_btn = QPushButton('Clear')
        self.submit_btn = QPushButton('Submit')

        for dialog_btn in [self.clear_btn, self.submit_btn]:
            dialog_btn.setSizePolicy(self.dialog_btn_size_policy)
            dialog_btn.setFocusPolicy(Qt.NoFocus)

        self.main_layout = QGridLayout()
        # important -- grid layout:  row, column, rowSpan(=1), columnSpan(=1), Qt.Alignment(=0)
        # important                                            row,
        # important                                              column,
        # important                                                  rowSpan,
        # important                                                     columnSpan
        # row 1
        self.main_layout.addWidget(self.task_label,        0, 0)
        self.main_layout.addWidget(self.category_label,    0, 2)
        self.main_layout.addWidget(self.importance_label,  0, 3, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.urgency_label,     0, 4, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.difficulty_label,  0, 5, 1, 1, Qt.AlignHCenter)
        # row 2
        self.main_layout.addWidget(self.task_input,        1, 0, 1, 2)
        self.main_layout.addWidget(self.category_dropdown, 1, 2, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.importance_input,  1, 3, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.urgency_input,     1, 4, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.difficulty_input,  1, 5, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.calendar_btn,      1, 6, 1, 1, Qt.AlignHCenter)
        self.main_layout.addWidget(self.weight_label,      1, 7, 1, 1, Qt.AlignHCenter)
        # row 3
        self.main_layout.addWidget(self.i_slider,          2, 3)
        self.main_layout.addWidget(self.u_slider,          2, 4)
        self.main_layout.addWidget(self.d_slider,          2, 5)
        self.main_layout.addWidget(self.calendar_widget,   2, 6)
        self.main_layout.addWidget(self.weight_calc,       2, 7, 1, 1, Qt.AlignHCenter)
        # row 4
        self.main_layout.addWidget(self.descr_label,       3, 0, 1, 2)
        # row 5
        self.main_layout.addWidget(self.descr_input, 4, 0, 1, 5)
        self.main_layout.addWidget(self.clear_btn, 4, 6)
        self.main_layout.addWidget(self.submit_btn, 4, 7)

        self.setLayout(self.main_layout)
        self.setWindowTitle("New Priority")

    def resizeEvent(self, event):  # To see what's going on
        new_width = self.width()
        new_height = self.height()
        log.debug("width: %s, height: %s\n" % (new_width, new_height))


##############
# PyDateEdit #
##############
class PyDateEdit(QDateEdit):
    """ Initialize base class
            Force use of the calendar popup
        Set default values for calendar properties
    """
    def __init__(self, *args):
        super(PyDateEdit, self).__init__(*args)

        self.setCalendarPopup(True)
        self.setDisplayFormat('yyyy-MM-dd')
        self.setDate(QDate.currentDate())
        self.__cw = None
        self.__first_day_of_week = Qt.Monday
        self.__grid_visible = False
        self.__h_header_format = QCalendarWidget.ShortDayNames
        self.__v_header_format = QCalendarWidget.ISOWeekNumbers
        self.__nav_bar_visible = True

    # Call event handler of base class
    def mousePressEvent(self, event):
        """ Call event handler of base class
                Get the calendar widget, if not already done
            Set the calendar properties
        """
        super(PyDateEdit, self).mousePressEvent(event)

        if not self.__cw:
            self.__cw = self.findChild(QCalendarWidget)
            if self.__cw:
                self.__cw.setFirstDayOfWeek(self.__first_day_of_week)
                self.__cw.setGridVisible(self.__grid_visible)
                self.__cw.setHorizontalHeaderFormat(self.__h_header_format)
                self.__cw.setVerticalHeaderFormat(self.__v_header_format)
                self.__cw.setNavigationBarVisible(self.__nav_bar_visible)

    # Make sure, the calendarPopup property is invisible in Designer
    def get_calendar_popup(self):
        """ Make sure, the calendarPopup property is invisible in Designer
        """
        return True
    calendarPopup = pyqtProperty(bool, fget=get_calendar_popup)

    # Property first_day_of_week: Qt::DayOfWeek
    def get_first_day_of_week(self):
        """ Property first_day_of_week: Qt::DayOfWeek
                Get: get_first_day_of_week()
            Set: set_first_day_of_week()
                Reset: reset_first_day_of_week()
        """
        return self.__first_day_of_week

    def set_first_day_of_week(self, day_of_week):
        if day_of_week != self.__first_day_of_week:
            self.__first_day_of_week = day_of_week
            if self.__cw:
                self.__cw.set_first_day_of_week(day_of_week)

    def reset_first_day_of_week(self):
        if self.__first_day_of_week != Qt.Monday:
            self.__first_day_of_week = Qt.Monday
            if self.__cw:
                self.__cw.set_first_day_of_week(Qt.Monday)

    first_day_of_week = pyqtProperty(Qt.DayOfWeek,
                                     fget=get_first_day_of_week,
                                     fset=set_first_day_of_week,
                                     freset=reset_first_day_of_week)

    # Property grid_visible: bool
    def is_grid_visible(self):
        """ Property grid_visible: bool
                Get: is_grid_visible()
            Set: set_grid_visible()
                Reset: reset_grid_visible()
        """
        return self.__grid_visible

    def set_grid_visible(self, show):
        if show != self.__grid_visible:
            self.__grid_visible = show
            if self.__cw:
                self.__cw.set_grid_visible(show)

    def reset_grid_visible(self):
        if self.__grid_visible:
            self.__grid_visible = False
            if self.__cw:
                self.__cw.set_grid_visible(False)

    grid_visible = pyqtProperty(bool,
                                fget=is_grid_visible,
                                fset=set_grid_visible,
                                freset=reset_grid_visible)

    # Property h_header_format: QCalendarWidget::HorizontalHeaderFormat
    def get_h_header_format(self):
        """ Property h_header_format: QCalendarWidget::HorizontalHeaderFormat
                Get: get_h_header_format()
            Set: set_h_header_format()
                Reset: reset_h_header_format()
        """
        return self.__h_header_format

    def set_h_header_format(self, format):
        if format != self.__h_header_format:
            self.__h_header_format = format
            if self.__cw:
                self.__cw.set_h_header_format(format)

    def reset_h_header_format(self):
        if self.__h_header_format != QCalendarWidget.ShortDayNames:
            self.__h_header_format = QCalendarWidget.ShortDayNames
            if self.__cw:
                self.__cw.set_h_header_format(QCalendarWidget.ShortDayNames)

    h_header_format = pyqtProperty(QCalendarWidget.HorizontalHeaderFormat,
                                   fget=get_h_header_format,
                                   fset=set_h_header_format,
                                   freset=reset_h_header_format)

    # Property v_header_format: QCalendarWidget::VerticalHeaderFormat
    def get_v_header_format(self):
        """ Property v_header_format: QCalendarWidget::VerticalHeaderFormat
                Get: get_v_header_format()
            Set: set_v_header_format()
                Reset: reset_v_header_format()
        """
        return self.__v_header_format

    def set_v_header_format(self, format):
        if format != self.__v_header_format:
            self.__v_header_format = format
            if self.__cw:
                self.__cw.set_v_header_format(format)

    def reset_v_header_format(self):
        if self.__v_header_format != QCalendarWidget.ISOWeekNumbers:
            self.__v_header_format = QCalendarWidget.ISOWeekNumbers
            if self.__cw:
                self.__cw.set_v_header_format(QCalendarWidget.ISOWeekNumbers)

    v_header_format = pyqtProperty(QCalendarWidget.VerticalHeaderFormat,
                                   fget=get_v_header_format,
                                   fset=set_v_header_format,
                                   freset=reset_v_header_format)

    # Property nav_bar_visible: bool
    def is_nav_bar_visible(self):
        """ Property nav_bar_visible: bool
                Get: is_nav_bar_visible()
            Set: set_nav_bar_visible()
                Reset: reset_nav_bar_visible()
        """
        return self.__nav_bar_visible

    def set_nav_bar_visible(self, visible):
        if visible != self.__nav_bar_visible:
            self.__nav_bar_visible = visible
            if self.__cw:
                self.__cw.set_nav_bar_visible(visible)

    def reset_nav_bar_visible(self):
        if not self.__nav_bar_visible:
            self.__nav_bar_visible = True
            if self.__cw:
                self.__cw.set_nav_bar_visible(True)

    nav_bar_visible = pyqtProperty(bool,
                                   fget=is_nav_bar_visible,
                                   fset=set_nav_bar_visible,
                                   freset=reset_nav_bar_visible)

#
# #============================================================================#
# # PyDateTimeEdit                                                             #
# #----------------------------------------------------------------------------#
# class PyDateTimeEdit(QDateTimeEdit):
#     #
#     # Initialize base class
#     # Force use of the calendar popup
#     # Set default values for calendar properties
#     #
#     def __init__(self, *args):
#         super(PyDateTimeEdit, self).__init__(*args)
#
#         self.setCalendarPopup(True)
#         self.__cw = None
#         self.__first_day_of_week = Qt.Monday
#         self.__grid_visible = False
#         self.__h_header_format = QCalendarWidget.ShortDayNames
#         self.__v_header_format = QCalendarWidget.ISOWeekNumbers
#         self.__nav_bar_visible = True
#
#     #
#     # Call event handler of base class
#     # Get the calendar widget, if not already done
#     # Set the calendar properties
#     #
#     def mousePressEvent(self, event):
#         super(PyDateTimeEdit, self).mousePressEvent(event)
#
#         if not self.__cw:
#             self.__cw = self.findChild(QCalendarWidget)
#             if self.__cw:
#                 self.__cw.setFirstDayOfWeek(self.__first_day_of_week)
#                 self.__cw.setGridVisible(self.__grid_visible)
#                 self.__cw.setHorizontalHeaderFormat(self.__h_header_format)
#                 self.__cw.setVerticalHeaderFormat(self.__v_header_format)
#                 self.__cw.setNavigationBarVisible(self.__nav_bar_visible)
#
#     #
#     # Make sure, the calendarPopup property is invisible in Designer
#     #
#     def get_calendar_popup(self):
#         return True
#     calendarPopup = pyqtProperty(bool, fget=get_calendar_popup)
#
#     #
#     # Property first_day_of_week: Qt::DayOfWeek
#     # Get: get_first_day_of_week()
#     # Set: set_first_day_of_week()
#     # Reset: reset_first_day_of_week()
#     #
#     def get_first_day_of_week(self):
#         return self.__first_day_of_week
#     def set_first_day_of_week(self, day_of_week):
#         if day_of_week != self.__first_day_of_week:
#             self.__first_day_of_week = day_of_week
#             if self.__cw:
#                 self.__cw.set_first_day_of_week(day_of_week)
#     def reset_first_day_of_week(self):
#         if self.__first_day_of_week != Qt.Monday:
#             self.__first_day_of_week = Qt.Monday
#             if self.__cw:
#                 self.__cw.set_first_day_of_week(Qt.Monday)
#     first_day_of_week = pyqtProperty(Qt.DayOfWeek,
#                                          fget=get_first_day_of_week,
#                                          fset=set_first_day_of_week,
#                                          freset=reset_first_day_of_week)
#
#     #
#     # Property grid_visible: bool
#     # Get: is_grid_visible()
#     # Set: set_grid_visible()
#     # Reset: reset_grid_visible()
#     #
#     def is_grid_visible(self):
#         return self.__grid_visible
#     def set_grid_visible(self, show):
#         if show != self.__grid_visible:
#             self.__grid_visible = show
#             if self.__cw:
#                 self.__cw.set_grid_visible(show)
#     def reset_grid_visible(self):
#         if self.__grid_visible != False:
#             self.__grid_visible = False
#             if self.__cw:
#                 self.__cw.set_grid_visible(False)
#     grid_visible = pyqtProperty(bool,
#                                       fget=is_grid_visible,
#                                       fset=set_grid_visible,
#                                       freset=reset_grid_visible)
#
#     #
#     # Property h_header_format: QCalendarWidget::HorizontalHeaderFormat
#     # Get: get_h_header_format()
#     # Set: set_h_header_format()
#     # Reset: reset_h_header_format()
#     #
#     def get_h_header_format(self):
#         return self.__h_header_format
#     def set_h_header_format(self, format):
#         if format != self.__h_header_format:
#             self.__h_header_format = format
#             if self.__cw:
#                 self.__cw.set_h_header_format(format)
#     def reset_h_header_format(self):
#         if self.__h_header_format != QCalendarWidget.ShortDayNames:
#             self.__h_header_format = QCalendarWidget.ShortDayNames
#             if self.__cw:
#                 self.__cw.set_h_header_format(QCalendarWidget.ShortDayNames)
#     h_header_format = pyqtProperty(QCalendarWidget.HorizontalHeaderFormat,
#                                                  fget=get_h_header_format,
#                                                  fset=set_h_header_format,
#                                                  freset=reset_h_header_format)
#
#     #
#     # Property v_header_format: QCalendarWidget::v_header_format
#     # Get: get_v_header_format()
#     # Set: set_v_header_format()
#     # Reset: reset_v_header_format()
#     #
#     def get_v_header_format(self):
#         return self.__v_header_format
#     def set_v_header_format(self, format):
#         if format != self.__v_header_format:
#             self.__v_header_format = format
#             if self.__cw:
#                 self.__cw.set_v_header_format(format)
#     def reset_v_header_format(self):
#         if self.__v_header_format != QCalendarWidget.ISOWeekNumbers:
#             self.__v_header_format = QCalendarWidget.ISOWeekNumbers
#             if self.__cw:
#                 self.__cw.set_v_header_format(QCalendarWidget.ISOWeekNumbers)
#     v_header_format = pyqtProperty(QCalendarWidget.v_header_format,
#                                                fget=get_v_header_format,
#                                                fset=set_v_header_format,
#                                                freset=reset_v_header_format)
#
#     #
#     # Property nav_bar_visible: bool
#     # Get: is_nav_bar_visible()
#     # Set: set_nav_bar_visible()
#     # Reset: reset_nav_bar_visible()
#     #
#     def is_nav_bar_visible(self):
#         return self.__nav_bar_visible
#     def set_nav_bar_visible(self, visible):
#         if visible != self.__nav_bar_visible:
#             self.__nav_bar_visible = visible
#             if self.__cw:
#                 self.__cw.set_nav_bar_visible(visible)
#     def reset_nav_bar_visible(self):
#         if self.__nav_bar_visible != True:
#             self.__nav_bar_visible = True
#             if self.__cw:
#                 self.__cw.set_nav_bar_visible(True)
#     nav_bar_visible = pyqtProperty(bool,
#                                                fget=is_nav_bar_visible,
#                                                fset=set_nav_bar_visible,
#                                                freset=reset_nav_bar_visible)


class Dialogs(QDialog):
    def __init__(self, parent=None):
        super(Dialogs, self).__init__(parent)

    def question_box(self, confirm_action, task):
        q_message = "%s '%s'?" % (confirm_action.upper(), task)
        reply = QMessageBox.question(self, "CONFIRM DB ACTION", q_message,
                                     QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes

    def db_error(self, failure, error_message):
        """ prompt message box on DB_model.py transaction error """
        log.debug("\n%s:\n\t%s\n" % (failure, error_message))
        QMessageBox.warning(self, failure, error_message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = InputDialog()
    dialog.show()
    sys.exit(app.exec_())
