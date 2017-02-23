#! /usr/bin/python
######################
# views\Delegates.py #
######################
from PyQt5.QtWidgets import QStyleOptionViewItem, QDateEdit
from PyQt5.QtSql import QSqlRelationalDelegate
from PyQt5.QtCore import Qt, QDate
(TASK, WEIGHT, CATEGORY, DESCRIPTION, IMPORTANCE, URGENCY, DIFFICULTY,
 DT_ADDED, DATE_DUE, DT_COMPLETE, STATUS, DT_ARCHIVED, PRIORITY_ID) = range(13)


class PriorityDelegate(QSqlRelationalDelegate):
    def __init__(self, parent=None):
        super(PriorityDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        """ This method will be called every time a particular cell is in view and that view
                is changed in some way. We ask the delegates parent (in this case a table view)
            if the index in question (the table cell) already has a widget associated with it.
                If not, create one with the text for this index and connect its clicked signal
            to a slot in the parent view so we are notified when its used and can do something."""
        my_option = QStyleOptionViewItem(option)
        if index.column() in [DT_ADDED, DATE_DUE, DT_COMPLETE, DT_ARCHIVED]:
            my_option.displayAlignment |= (Qt.AlignRight | Qt.AlignVCenter)
        # if index.column() == STATUS:
        #     my_option.displayAlignment |= (Qt.AlignJustify | Qt.AlignVCenter)
        QSqlRelationalDelegate.paint(self, painter, my_option, index)

    def createEditor(self, parent, option, index):
        if index.column() in [TASK, WEIGHT, DT_ADDED, DT_COMPLETE, STATUS]:
            return  # Read-only
        if index.column() == DATE_DUE:
            editor = QDateEdit(parent)
            editor.setMinimumDate(QDate.currentDate())
            editor.setDisplayFormat("yyyy-MM-dd")
            editor.setCalendarPopup(True)
            editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            return editor
        else:
            return QSqlRelationalDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == DATE_DUE:
            date = index.model().data(index, Qt.DisplayRole)
            editor.setDate(QDate.fromString(date, 'yyyy-MM-dd'))
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == DATE_DUE:
            model.setData(index, editor.date())
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model, index)


class DetailDelegate(QSqlRelationalDelegate):
    def __init__(self, parent=None):
        super(DetailDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        my_option = QStyleOptionViewItem(option)
        QSqlRelationalDelegate.paint(self, painter, my_option, index)

    def createEditor(self, parent, option, index):
        if index.column() == DESCRIPTION:
            return  # todo - DESCRIPTION is read-only - consider changing once grid-submission enabled
        else:
            return QSqlRelationalDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        QSqlRelationalDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        QSqlRelationalDelegate.setModelData(self, editor, model, index)


# class ButtonDelegate(QItemDelegate):
#     """ A delegate that places a fully functioning QPushButton in every
#             cell of the column to which it's applied """
#
#     def __init__(self, parent):
#         """ The parent is not an optional argument for the delegate as
#                 we need to reference it in the paint method (see below)"""
#         QItemDelegate.__init__(self, parent)
#
#     def paint(self, painter, option, index):
#         """ This method will be called every time a particular cell is in view and that view
#                 is changed in some way. We ask the delegates parent (in this case a table view)
#             if the index in question (the table cell) already has a widget associated with it.
#                 If not, create one with the text for this index and connect its clicked signal
#             to a slot in the parent view so we are notified when its used and can do something."""
#         if not self.parent().indexWidget(index):
#             self.parent().setIndexWidget(
#                 index, QPushButton(index.data(),
#                                    self.parent(),
#                                    clicked=self.parent().cellButtonClicked))
#

# class ViewDelegate(QtWidgets.QItemDelegate):
#     def __init__(self, parent, table):
#         super(ViewDelegate, self).__init__(parent)
#         self.table = table
#
#     def sizeHint(self, option, index):
#         # Get full viewport size
#         table_size = self.viewport().size()
#         gw = 1  # Grid line width
#         rows = self.rowCount() or 1
#         cols = self.columnCount() or 1
#         width = (table_size.width() - (gw * (cols - 1))) / cols
#         height = (table_size.height() - (gw * (rows - 1))) / rows
#         return QtCore.QSize(width, height)

#
# class Window(QtGui.QWidget):
#     def __init__(self, rows, columns):
#         super(Window, self).__init__()
#         self.lay = QtGui.QVBoxLayout()
#         self.setLayout(self.lay)
#         self.table = QtGui.QTableWidget(rows, columns, self)
#         self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.lay.addWidget(self.table)
#         self.delegate = MyDelegate(self, self.table)
#         self.table.setItemDelegate(self.delegate)
#
#     def showEvent(self, event):
#         super(Window, self).showEvent(event)
#         self.resizeTable()
#
#     def resizeTable(self):
#         self.table.resizeRowsToContents()
#         self.table.resizeColumnsToContents()
#
#     def resizeEvent(self, event):
#         super(Window, self).resizeEvent(event)
#         self.resizeTable()
