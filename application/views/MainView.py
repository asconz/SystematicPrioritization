#! /usr/bin/python
#####################
# views\MainView.py #
#####################
"""
The observer pattern is a software design pattern in which an object, called
the subject, maintains a list of its dependents, called observers, and notifies
them automatically of any state changes, usually by calling one of their methods.

    It is mainly used to implement distributed event handling systems.

The Observer pattern is also a key part in the familiar model–view–controller (MVC)
architectural pattern.

The observer pattern can cause memory leaks, known as the lapsed listener problem,
because in basic implementation it requires both explicit registration and explicit
de-registration, as in the dispose pattern, because the subject holds strong
references to the observers, keeping them alive.

    This can be prevented by the subject holding weak references to the observers.
"""
import logging
from PyQt5.QtWidgets import (QMainWindow, QTableView, QAbstractScrollArea, QSystemTrayIcon, QMenu, QAction, QSlider,
                             QLabel, QToolButton, QToolBox, QWidget, QButtonGroup, QFontComboBox)
from PyQt5.QtCore import QDate, QMargins, Qt, QCoreApplication, QMetaObject, QSize
from PyQt5.QtGui import QPixmap, QIcon
from Delegates import PriorityDelegate, DetailDelegate
from Dialogs import InputDialog
from ui_MainView import Ui_MainWindow
log = logging.getLogger('main_view')
(TASK, WEIGHT, CATEGORY, DESCRIPTION, IMPORTANCE, URGENCY, DIFFICULTY,
 DT_ADDED, DATE_DUE, DT_COMPLETE, STATUS, DT_ARCHIVED, PRIORITY_ID) = range(13)


class MainView(QMainWindow):
    """ Contains logic to connect to layout-widget signals.
            Calls/passes basic info to sub-methods, heavier logic in controller.
        View can then import relevant classes from layouts. """
    #### GET WIDGET PROPERTY VALUES ####
    """## input_dialog ##"""
    @property
    def task_input(self):
        return self.input_dialog.task_input.text()

    @property
    def weight_calc(self):
        return self.input_dialog.weight_calc.text()

    @property
    def importance_input(self):
        return self.input_dialog.importance_input.text()

    @property
    def i_slider(self):
        return self.input_dialog.i_slider.value()

    @property
    def urgency_input(self):
        return self.input_dialog.urgency_input.text()

    @property
    def u_slider(self):
        return self.input_dialog.u_slider.value()

    @property
    def difficulty_input(self):
        return self.input_dialog.difficulty_input.text()

    @property
    def d_slider(self):
        return self.input_dialog.d_slider.value()

    @property
    def cat_dropdown(self):
        return self.input_dialog.category_dropdown.currentText()

    @property
    def descr_input(self):
        return self.input_dialog.descr_input.text()

    @property
    def due_date(self):
        return self.input_dialog.calendar_widget.date()

    """## MainWindow ##"""
    @property
    def selected_row_index(self):
        row_index = self.ui.priority_view.currentIndex().row()
        log.debug("@GET selected_row_index() = %s" % row_index)
        return row_index

    #### SET WIDGET PROPERTY VALUES ####
    """## input_dialog ##"""
    @task_input.setter
    def task_input(self, value):
        self.input_dialog.task_input.setText(value)

    @weight_calc.setter
    def weight_calc(self, value):
        self.input_dialog.weight_calc.setText(str(value))

    @importance_input.setter
    def importance_input(self, value):
        self.input_dialog.importance_input.setText(str(value))

    @urgency_input.setter
    def urgency_input(self, value):
        self.input_dialog.urgency_input.setText(str(value))

    @difficulty_input.setter
    def difficulty_input(self, value):
        self.input_dialog.difficulty_input.setText(str(value))

    @i_slider.setter
    def i_slider(self, value):
        self.input_dialog.i_slider.setValue(value)

    @u_slider.setter
    def u_slider(self, value):
        self.input_dialog.u_slider.setValue(value)

    @d_slider.setter
    def d_slider(self, value):
        self.input_dialog.d_slider.setValue(value)

    @cat_dropdown.setter
    def cat_dropdown(self, cat_val):
        if cat_val is not None:
            cat_text = [key for key, value in self.model.category_dict.items() if value == cat_val][0]
            self.input_dialog.category_dropdown.setCurrentText(cat_text)

    @descr_input.setter
    def descr_input(self, value):
        self.input_dialog.descr_input.setText(value)

    @due_date.setter
    def due_date(self, date):
        if self.model.update_id:
            if date:
                self.input_dialog.calendar_btn.setChecked(True)
                self.input_dialog.calendar_widget.setHidden(False)
                self.input_dialog.calendar_widget.setDate(QDate.fromString(date, 'yyyy-MM-dd'))
            else:
                self.input_dialog.calendar_widget.setDate(QDate.currentDate())
        elif date:
            self.input_dialog.calendar_widget.setDate(QDate.fromString(date, 'yyyy-MM-dd'))
        else:
            self.input_dialog.calendar_widget.setDate(QDate.currentDate())

    def __init__(self, model, main_ctrl):
        log.debug("MainView.py init")
        # log.debug(dir())
        self.model = model
        self.main_ctrl = main_ctrl
        super(MainView, self).__init__()
        self.perspective, self.category, self.slider_cleared = 'Active', None, 5
        self.indicate_filters = QLabel()
        # self.systray_icon()
        self.ui = Ui_MainWindow()
        self.input_dialog = InputDialog(self)
        self.priority_delegate = PriorityDelegate()
        self.detail_delegate = DetailDelegate()
        self.build_ui()
        # self.create_toolbars()
        #### Register with model for announcements ####
        self.model.subscribe_update_func(self.update_ui_from_model)
        self.model.subscribe_update_func(self.init_table_views)
        self.model.subscribe_refresh_detail_filter(self.detail_view_init)
        self.show()
        self.resizeEvent(self)

    def build_ui(self):
        self.ui.setupUi(self)
        self.ui.perspective_filter_frame.setHidden(True)
        #### Set Qt Data Models for Views ####
        self.init_table_views()
        self.ui.status_bar.addPermanentWidget(self.indicate_filters)
        self.refresh_status_bar()
        # self.perspectiveToolButton.setMenu(
        #     self.createPerspectiveMenu(self.perspective_changed, self.ui.Active))
        # self.ui.TaskPerspectiveToolBar.addWidget(self.ui.Active)
        # self.ui.TaskPerspectiveToolBar.addWidget(self.ui.Overdue)
        # self.ui.TaskPerspectiveToolBar.addWidget(self.ui.Archived)
        # self.ui.TaskPerspectiveToolBar.addWidget(self.ui.Completed)
        # self.ui.TaskPerspectiveToolBar.addWidget(self.ui.ByDate)
        # self.ui.TaskPerspectiveToolBar.setHidden(True)
        self.create_filter_menus()
        #### Connect signals to controller event methods ####
        """## input_dialog ##"""
        self.input_dialog.task_input.textEdited.connect(self.on_input_value)
        self.input_dialog.descr_input.textEdited.connect(self.on_input_value)
        self.input_dialog.category_dropdown.currentTextChanged.connect(self.on_input_value)
        for slider in [self.input_dialog.i_slider, self.input_dialog.u_slider, self.input_dialog.d_slider]:
            slider.valueChanged.connect(self.on_slider_change)
        self.input_dialog.calendar_btn.clicked.connect(self.on_dialog_calendar_btn)
        self.input_dialog.calendar_widget.dateChanged.connect(self.on_dialog_due_date)
        self.input_dialog.clear_btn.clicked.connect(self.on_clear_btn)
        self.input_dialog.submit_btn.clicked.connect(self.on_submit_btn)
        """## MainWindow ##"""
        # current work to combine db_action buttons - 02-09
        # # self.ui.AddPriority.clicked.connect(self.db_grid_btn_click)
        # # self.ui.EditPriority.clicked.connect(self.db_grid_btn_click)
        # for action_btn in [self.ui.AddPriority, self.ui.MarkComplete, self.ui.EditPriority,
        #                    self.ui.ArchivePriority, self.ui.DeletePriority]:
        #     action_btn.clicked.connect(self.on_db_action_btn)
        self.ui.AddPriority.clicked.connect(self.db_grid_btn_click)
        self.ui.EditPriority.clicked.connect(self.db_grid_btn_click)
        for action_btn in [self.ui.DeletePriority, self.ui.MarkComplete, self.ui.ArchivePriority]:
            action_btn.clicked.connect(self.on_db_action_btn)
        for perspective_icon in [self.ui.Active, self.ui.Overdue, self.ui.Archived, self.ui.Completed, self.ui.ByDate]:
            perspective_icon.clicked.connect(self.select_perspective)
        for category_icon in [self.ui.All, self.ui.Career, self.ui.Finance, self.ui.Projects, self.ui.Misc]:
            category_icon.clicked.connect(self.select_category)
        self.ui.PerspectiveToolButton.clicked.connect(self.on_filter_frame)
        self.set_default_model_values()

    def init_table_views(self):
        self.priority_view_init()
        self.detail_view_init()
        if not self.main_ctrl.detail_id_check_new_filter():
            self.priority_selected(self.ui.priority_view.currentIndex())
            # rechecks for selected priority after new filters
        # self.resizeWindowToColumns()

    def priority_view_init(self):
        self.ui.priority_view.setModel(self.model.priority_model)
        self.ui.priority_view.setItemDelegate(self.priority_delegate)
        # self.ui.priority_view.setSelectionMode(QTableView.SingleSelection)
        # self.ui.priority_view.setSelectionBehavior(QTableView.SelectRows)
        self.ui.priority_view.verticalHeader().setFixedWidth(28)
        self.display_fields_by_filter()
        # self.ui.priority_view.resizeColumnsToContents()
        # self.ui.priority_view.horizontalHeader().setStretchLastSection(True)
        # self.ui.priority_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        # self.ui.priority_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.ui.priority_view.horizontalHeader().setVisible(self.model.priority_model.rowCount() > 0)
        self.ui.priority_view.selectionModel().currentRowChanged.connect(self.priority_selected)
        self.model.priority_model.select()

    def display_fields_by_filter(self):
        self.priority_fields_by_perspective()
        # self.priority_fields_by_category()
        self.priority_field_widths()

    def priority_fields_by_perspective(self):
        column_count = self.model.priority_model.columnCount()
        for col in range(column_count):
            if self.perspective in ['Active', 'Overdue']:
                if col in [DT_COMPLETE, DT_ARCHIVED, STATUS]:
                    self.ui.priority_view.setColumnHidden(col, True)
                else:
                    self.ui.priority_view.setColumnHidden(col, False)
            elif self.perspective == 'Archived':
                if col in [DATE_DUE, DT_COMPLETE, STATUS]:
                    self.ui.priority_view.setColumnHidden(col, True)
                else:
                    self.ui.priority_view.setColumnHidden(col, False)
            elif self.perspective == 'Completed':
                if col in [DATE_DUE, DT_ARCHIVED, STATUS]:
                    self.ui.priority_view.setColumnHidden(col, True)
                else:
                    self.ui.priority_view.setColumnHidden(col, False)
            else:
                if col in [DATE_DUE, DT_ARCHIVED]:
                    self.ui.priority_view.setColumnHidden(col, True)
                else:
                    self.ui.priority_view.setColumnHidden(col, False)

            if col in [DESCRIPTION, PRIORITY_ID]:
                self.ui.priority_view.setColumnHidden(col, True)

    # def priority_fields_by_category(self):
    #     if self.category:
    #         self.ui.priority_view.setColumnHidden(CATEGORY, True)
    #     else:
    #         self.ui.priority_view.setColumnHidden(CATEGORY, False)

    def priority_field_widths(self):
        print(self.ui.priority_view_title.text())
        log.debug(self.ui.priority_view_title.text())
        columns = self.model.priority_model.columnCount()
        if not self.perspective:
            self.ui.priority_view.setColumnWidth(TASK, 200)
            self.ui.priority_view.setColumnWidth(STATUS, 85)
            self.ui.priority_view.setColumnWidth(IMPORTANCE, 85)
            for col in [URGENCY, DIFFICULTY]:
                self.ui.priority_view.setColumnWidth(col, 70)
            for col in [DT_ADDED, DT_COMPLETE]:
                self.ui.priority_view.setColumnWidth(col, 85)
        else:
            self.ui.priority_view.setColumnWidth(TASK, 250)
            for col in [IMPORTANCE, URGENCY, DIFFICULTY]:
                self.ui.priority_view.resizeColumnToContents(col)
            for col in [DT_ADDED, DATE_DUE, DT_COMPLETE, DT_ARCHIVED]:
                if not self.ui.priority_view.isColumnHidden(col):
                    self.ui.priority_view.setColumnWidth(col, 95)

        self.ui.priority_view.setColumnWidth(WEIGHT, 61)
        self.ui.priority_view.setColumnWidth(CATEGORY, 74)

        for col in range(columns):
            print("\t%s - %s" % (col, self.ui.priority_view.columnWidth(col)))
            log.debug("\t%s - %s" % (col, self.ui.priority_view.columnWidth(col)))

    def detail_view_init(self):
        self.ui.detail_view.setModel(self.model.detail_model)
        self.ui.detail_view.setItemDelegate(self.detail_delegate)
        self.detail_fields_by_filter()
        self.ui.detail_view.setStyleSheet("""QHeaderView::section {
                                                background-color: #f2f2f2;
                                                border-color: transparent;
                                            }""")
        self.ui.detail_view.resizeColumnsToContents()
        if self.model.detail_model.rowCount() > 0:
            self.ui.detail_view_group_box.setMaximumHeight(85)
            self.ui.detail_view.setMaximumHeight(65)
        else:
            self.ui.detail_view_group_box.setMaximumHeight(50)
            self.ui.detail_view.setMaximumHeight(30)
        self.ui.detail_view.horizontalHeader().setVisible(self.model.detail_model.rowCount() > 0)
        self.model.detail_model.select()

        self.title_views_by_filter()

    def detail_fields_by_filter(self):
        column_count = self.model.detail_model.columnCount()
        if not self.ui.detail_view.horizontalHeader().sectionsMoved():
            self.ui.detail_view.horizontalHeader().moveSection(DT_ADDED, DESCRIPTION)
        for col in range(column_count):
            if col not in [DESCRIPTION, DT_ADDED]:
                self.ui.detail_view.setColumnHidden(col, True)

    def title_views_by_filter(self):
        dv_title = self.main_ctrl.task_name
        self.ui.detail_view_group_box.setTitle(dv_title)
        pv_perspective = self.perspective if self.perspective else None
        pv_category = self.category if self.category else 'All'
        if pv_perspective:
            pv_title = pv_perspective + " Priorities - " + pv_category
        else:
            pv_title = "Priorities by Date - " + pv_category
        self.ui.priority_view_title.setText(pv_title)
        log.debug(pv_title)

    def refresh_status_bar(self):
        status_bar_c = " -  %s" % self.category if self.category else " - All"
        if self.perspective == 'Active':
            status_bar_p = "Active and Overdue"
        else:
            status_bar_p = "%s" % self.perspective if self.perspective else "By Date"
        self.indicate_filters.setText("%s %s " % (status_bar_p, status_bar_c))

    def resizeWindowToColumns(self):
        # later - dynamic column widths fit to window size
        pass
        # for col in [DT_ADDED, DATE_DUE, DT_COMPLETE, DT_ARCHIVED]:
        #     self.ui.priority_view.setColumnWidth(col, 100)
        # self.ui.priority_view.setColumnWidth(TASK, 250)
        # for col in [WEIGHT, CATEGORY, IMPORTANCE, URGENCY, DIFFICULTY, STATUS]:
        #     self.ui.priority_view.setColumnWidth(col, 85)

        #     log.debug("BEFORE: PRIORITY_VIEW_SIZE = %s" % view_size)
        #     row_count = self.model.priority_model.rowCount()
        #     column_count = self.model.priority_model.columnCount()
        #     self.status_message(message="Priority Rows/Columns = (%s, %s)" % (row_count, column_count))
        #     # log.debug("DEBUG: resizeWindowToColumns")
        #     current_width = self.size().width()
        #     p_view_width = self.ui.priority_view.size().width()
        #     p_header_width = self.ui.priority_view.horizontalHeader().length()
        #     vt_header_width = self.ui.priority_view.verticalHeader().width()
        #     p_scroll_margin = self.ui.priority_view.autoScrollMargin()
        #     view_header_difference = p_header_width - p_view_width + p_scroll_margin * 2 + vt_header_width + 9
        #     new_view_width = current_width + view_header_difference
        #     vt_scroll_width = self.ui.priority_view.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        #     log.debug("\nWindow-width = %s" % current_width)
        #     log.debug("p_view_width = %s" % p_view_width)
        #     log.debug("p_header_width = %s" % p_header_width)
        #     log.debug("\n\t\tvt_header_width = %s\n" % vt_header_width)
        #     log.debug("\tvt_scroll_width = %s" % vt_scroll_width)
        #     log.debug("\tp_scroll_margin = %s" % p_scroll_margin)
        #     log.debug("Difference (to adjust) = %s" % view_header_difference)
        #     log.debug("New Width: %s\n" % new_view_width)
        #     self.resize(new_view_width, self.height())
        #     view_size = self.ui.priority_view.viewport().size()
        #     log.debug("AFTER: PRIORITY_VIEW_SIZE = %s" % view_size)
        #     if new_detail_width > new_view_width:
        #         self.resize(new_detail_width, self.height())
        #     else:
        #         self.resize(new_view_width, self.height())
        #
        # # def showEvent(self, event):
        # #     super(Window, self).showEvent(event)
        # #     self.resizeTable()
        #
        # # def resizeTable(self):
        # #     self.table.resizeRowsToContents()
        # #     self.table.resizeColumnsToContents()
        # def resizeEvent(self, event):  # To see what's going on
        #     self.status_message(message="Size set to (%s, %s)" % (event.size().width(), event.size().height()))
        #     new_vt_header_width = self.ui.priority_view.verticalHeader().width()
        #     log.debug("new_vt_header_width = %s\n" % new_vt_header_width)
        #
        # def resizeEvent(self, event):
        #     super(Window, self).resizeEvent(event)
        #     self.resizeTable()
        #
        #         log.debug("MainWindow/centralwidget width = %s/%s" %
        #           (self.size().width(), self.ui.centralwidget.size().width()))
        #     log.debug("\tcontainer_frame/priority_db_frame width = %s/%s" %
        #           (self.ui.container_frame.size().width(), self.ui.priority_db_frame.size().width()))

    def resizeEvent(self, event):  # To see what's going on
        log.debug("resizeEvent: now (%s, %s)" % (event.size().width(), event.size().height()))
        log.debug("priority_view width: %s" % self.ui.priority_view.width())
        log.debug("h-header width: %s" % self.ui.priority_view.horizontalHeader().length())
        log.debug("v-header width: %s" % self.ui.priority_view.verticalHeader().width())
        log.debug("p_view frameWidth: %s" % self.ui.priority_view.frameWidth())
        log.debug("autoScrollMargin: %s" % self.ui.priority_view.autoScrollMargin())
        log.debug("horizontalScrollBar width: %s" % self.ui.priority_view.horizontalScrollBar().width())
        log.debug("verticalScrollBar width: %s" % self.ui.priority_view.verticalScrollBar().width())
        log.debug("view_size: %s" % self.ui.priority_view.viewport().size())

    def set_default_model_values(self):
        """ Set initial model values from ui_MainView """
        self.model.importance_input = self.importance_input
        self.model.urgency_input = self.urgency_input
        self.model.difficulty_input = self.difficulty_input
        self.model.i_slider = self.i_slider
        self.model.u_slider = self.u_slider
        self.model.d_slider = self.d_slider
        # self.model.cat_dropdown_index = self.cat_dropdown_index

    def update_ui_from_model(self):
        """ Refresh displayed values on Model-announcement """
        self.task_input = self.model.task_input
        self.weight_calc = self.model.weight_calc
        self.importance_input = self.model.importance_input
        self.urgency_input = self.model.urgency_input
        self.difficulty_input = self.model.difficulty_input
        self.i_slider = self.model.i_slider
        self.u_slider = self.model.u_slider
        self.d_slider = self.model.d_slider
        self.cat_dropdown = self.model.cat_dropdown_index
        self.descr_input = self.model.descr_input
        self.due_date = self.model.date_due
        self.perspective = self.model.perspective
        self.category = self.model.category_filter
        # todo - add selected_row_index setter for consistency across views (w detail-filter check above)

    #### widget signal event functions ####
    """## input_dialog ##"""
    def on_input_value(self, text):
        sender_name = self.sender().objectName()
        self.main_ctrl.change_input_value(sender_name, text)

    def on_slider_change(self):
        self.main_ctrl.change_weight_metrics(self.i_slider, self.u_slider, self.d_slider)
        self.main_ctrl.calculate_weight()

    def on_clear_btn(self):
        """ Re-implement input_dialog default values"""
        self.clear_sliders()
        self.main_ctrl.click_clear_btn()
        self.input_dialog.calendar_btn.setChecked(False)
        self.input_dialog.calendar_widget.setHidden(True)
        self.input_dialog.setWindowTitle('New Priority')
        self.status_message(message='Inputs Cleared')

    def clear_sliders(self):
        self.i_slider = self.slider_cleared
        self.u_slider = self.slider_cleared
        self.d_slider = self.slider_cleared

    def on_dialog_calendar_btn(self):
        if self.input_dialog.calendar_btn.isChecked():
            self.input_dialog.calendar_widget.setHidden(False)
        else:
            self.input_dialog.calendar_widget.setHidden(True)
            self.main_ctrl.clear_due_date()

    def on_dialog_due_date(self, date):
        if not self.input_dialog.calendar_widget.isHidden():
            self.main_ctrl.due_date_change(QDate.toString(date, 'yyyy-MM-dd'))
        else:
            self.main_ctrl.clear_due_date()

    def on_submit_btn(self):
        self.main_ctrl.click_submit_btn()
        self.on_clear_btn()
        self.status_message(self.main_ctrl.status)
        # todo: self.sleep(2) -- allow user to see result before window close
        # todo - or consider dialog confirmation message (post input window close)
        self.input_dialog.close()

    """## MainWindow ##"""
    def select_perspective(self):
        sender_name = self.sender().objectName()
        self.perspective_filter_changed(sender_name)

    def perspective_filter_changed(self, sender_name):
        p_filter = sender_name if not sender_name == 'ByDate' else None
        self.main_ctrl.change_perspective_filter(p_filter)
        self.set_perspective_tool_button(sender_name)
        self.refresh_status_bar()

    def create_filter_menus(self):
        p_filter_icon = QIcon()
        p_filter_icon.addPixmap(QPixmap(":/Active.png"), QIcon.Normal, QIcon.Off)
        self.ui.PerspectiveToolButton.setIcon(p_filter_icon)
    # def create_toolbars(self):
    #     log.debug("debug createToolbars")
    #     self.perspective_tool_button = QToolButton()
    #     self.perspective_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
    #     self.perspective_tool_button.setMenu(
    #             self.create_perspective_menu(self.perspective_changed, 'Active'))
    #     self.text_action = self.perspective_tool_button.menu().defaultAction()
    #     self.perspective_tool_button.setIcon(
    #         self.create_perspective_icon(perspective='Active'))
    #     self.perspective_tool_button.setAutoFillBackground(True)
    #     # self.perspective_tool_button.clicked.connect(self.textButtonTriggered)
    #
    #     self.perspectiveToolBar = self.addToolBar("Perspective")
    #     self.perspectiveToolBar.addWidget(self.perspective_tool_button)
    #
    # def perspective_changed(self, sender_name):
    #     self.text_action = self.sender()
    #     self.perspective_tool_button.setIcon(
    #             self.create_perspective_icon(self.text_action))
    #     # self.textButtonTriggered()
    #
    # def create_perspective_menu(self, slot, default_perspective):
    #     perspectives = [self.ui.Active, self.ui.Overdue, self.ui.Archived, self.ui.Completed, self.ui.ByDate]
    #     names = ["Active", "Overdue", "Archived", "Completed", "ByDate"]
    #
    #     perspective_menu = QMenu(self)
    #     for perspective, name in zip(perspectives, names):
    #         action = QAction(self.create_perspective_icon(perspective), name, self,
    #                          triggered=slot)
    #         # action.setData(QIcon(perspective))
    #         perspective_menu.addAction(action)
    #         if perspective == default_perspective:
    #             perspective_menu.setDefaultAction(action)
    #     return perspective_menu
    #
    # def create_perspective_icon(self, perspective):
    #     p_filter_icon = QIcon()
    #     p_filter_icon.addPixmap(QPixmap(":/%s.png" % perspective), QIcon.Normal, QIcon.Off)
    #     return QIcon(p_filter_icon)

    def set_perspective_tool_button(self, perspective):
        p_filter_icon = QIcon()
        p_filter_icon.addPixmap(QPixmap(":/%s.png" % perspective), QIcon.Normal, QIcon.Off)
        self.ui.PerspectiveToolButton.setIcon(p_filter_icon)
        if not perspective == 'ByDate':
            self.ui.PerspectiveToolButton.setText("%s Priorities" % perspective)
        else:
            self.ui.PerspectiveToolButton.setText("Priorities By Date")

    def select_category(self):
        sender_name = self.sender().objectName()
        self.category_filter_changed(sender_name)

    def category_filter_changed(self, sender_name):
        # if sender_name == 'All' and self.ui.All.isChecked():
        #     self.on_clear_btn()  # important - check if All.isChecked BEFORE here
        c_filter = sender_name if not sender_name == 'All' else None
        self.main_ctrl.change_category_filter(c_filter)
        # later: # self.category_tool_button(sender_name)
        self.refresh_status_bar()

    def priority_selected(self, index):
        self.enable_action_buttons(index)
        self.main_ctrl.change_row_selection(index)
        self.status_message(self.main_ctrl.status)

    def enable_action_buttons(self, index):
        for btn in [self.ui.MarkComplete, self.ui.EditPriority,
                    self.ui.ArchivePriority, self.ui.DeletePriority]:
            if not index.isValid():
                btn.setEnabled(False)
            elif self.perspective == 'Completed':
                btn.setEnabled(True) if not btn == self.ui.MarkComplete else btn.setEnabled(False)
            elif self.perspective == 'Archived':
                btn.setEnabled(True) if not btn == self.ui.ArchivePriority else btn.setEnabled(False)
            else:
                btn.setEnabled(True)

    def db_grid_btn_click(self):
        sender_text = self.sender().text()
        self.input_dialog.calendar_btn.setChecked(False)
        self.input_dialog.calendar_widget.setHidden(True)
        if sender_text == 'Add Priority':
            self.input_dialog.exec_()
        if sender_text == 'Edit Priority':
            self.on_edit_priority_btn()

    def on_db_action_btn(self):
        action = self.sender().text()
        if not self.selected_row_index == -1:
            row_index = self.selected_row_index
            self.main_ctrl.send_db_action(row_index, action)
            self.status_message(self.main_ctrl.status)
        else:
            self.status_message(message = "%s Priority: No Selected Row" % action)

        # current work to combine db_action buttons - 02-09
        # def on_db_action_btn(self):
        #     action = self.sender().text()
        #     if action == 'Add':
        #         self.input_dialog.exec_()
        #     elif self.selected_row_index == -1:
        #         self.status_message(message="%s Priority: No Selected Row" % action)
        #     else:
        #         row_index = self.selected_row_index
        #         self.main_ctrl.send_db_action(row_index, action)
        #         self.status_message(self.main_ctrl.status)

    def on_edit_priority_btn(self):
        to_edit_index = self.selected_row_index
        if not to_edit_index == -1:
            record = self.model.priority_model.record(to_edit_index)
            self.input_dialog.setWindowTitle('Edit Priority: %s' % record.value('TASK'))
            if record.value('DATE_DUE'):
                self.input_dialog.calendar_btn.setChecked(False)
                self.input_dialog.calendar_widget.setHidden(True)
            self.status_message(message="Edit Priority: '%s'" % record.value('TASK'))
            self.main_ctrl.click_edit_priority_btn(record)
            self.input_dialog.exec_()
        else:
            self.status_message(message = "Edit Priority: No Selected Row")

    def on_filter_frame(self):
        sender_name = self.sender().objectName()
        if sender_name == 'PerspectiveToolButton':
            log.debug("on_filter_frame - Perspective")
            if self.ui.perspective_filter_frame.isHidden():
                self.ui.perspective_filter_frame.setHidden(False)
            else:
                self.ui.perspective_filter_frame.setHidden(True)
            log.debug("Hidden = %s" % self.ui.perspective_filter_frame.isHidden())

    def status_message(self, message):
        self.ui.status_bar.showMessage(message)
        log.debug("status_message: %s" % message)

    def systray_icon(self):
        systray_icon = QIcon("PrioritizationAppIcon.png")
        systray = QSystemTrayIcon(systray_icon, self)
        menu = QMenu()
        restore = QAction("Restore", self)
        close = QAction("Close", self)
        menu.addActions([restore, close])
        systray.setContextMenu(menu)
        systray.show()
        # systray.showMessage("Priority Manager",
        #                     "This is a test notification for BingDaddy's Priority App!",
        #                     QSystemTrayIcon.NoIcon)
        close.triggered.connect(self.close)

    def show_context_menu(self, position):
        # menu = QMenu(self)
        # archive = QAction("Archive", self)
        # menu.addAction(archive)
        # archive.triggered.connect(self.on_archive_btn)
        # menu.popup(self.on_archive_btn.mapToGlobal(position))
        pass


class JumpSlider(QSlider):  # later - implement for improved slider tracking
    # def mousePressEvent(self, ev):
    #     """ Jump to click position """
    #     self.setValue(
    #         QStyle.sliderValueFromPosition(
    #             self.minimum(), self.maximum(), ev.x(), self.width()))
    # def mouseMoveEvent(self, ev):
    #     """ Jump to pointer position while moving """
    #     self.setValue(
    #         QStyle.sliderValueFromPosition(
    #             self.minimum(), self.maximum(), ev.x(), self.width()))
    pass
