#! /usr/bin/python
################
# models\DB.py #
################
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlTableModel, QSqlDatabase, QSqlQuery, QSql
from Dialogs import Dialogs
log = logging.getLogger('DB')
(TASK, WEIGHT, CATEGORY, DESCRIPTION, IMPORTANCE, URGENCY, DIFFICULTY,
 DT_ADDED, DATE_DUE, DT_COMPLETE, STATUS, DT_ARCHIVED, PRIORITY_ID) = range(13)
db_actions = {'Mark Active': '1', 'Archive': '3', 'Mark Complete': '4', 'Delete': '5'}


class PriorityModel(QSqlRelationalTableModel):
    """ Contains data variables and logic to announce when updated by controller.
            Model.announce_update calls registered functions to refresh view (e.g.MainView.update_ui_from_model)."""
    def __init__(self, perspective, category):
        super(PriorityModel, self).__init__()
        self.setTable('priority')
        self.setRelation(CATEGORY,
                         QSqlRelation("category", "CATEGORY_ID", "CATEGORY"))
        self.setRelation(STATUS,
                         QSqlRelation("status", "STATUS_ID", "STATUS"))
        self.setRelation(DT_ARCHIVED,
                         QSqlRelation("history", "HIST_ID", "DT_MODIFIED"))
        self.setHeaderData(TASK, Qt.Horizontal, "Task")
        self.setHeaderData(WEIGHT, Qt.Horizontal, "Weight")
        self.setHeaderData(CATEGORY, Qt.Horizontal, "Category")
        self.setHeaderData(DESCRIPTION, Qt.Horizontal, "Description")
        self.setHeaderData(IMPORTANCE, Qt.Horizontal, "Importance")
        self.setHeaderData(URGENCY, Qt.Horizontal, "Urgency")
        self.setHeaderData(DIFFICULTY, Qt.Horizontal, "Difficulty")
        self.setHeaderData(DT_ADDED, Qt.Horizontal, "Date Added")
        self.setHeaderData(DATE_DUE, Qt.Horizontal, "Date Due")
        self.setHeaderData(DT_COMPLETE, Qt.Horizontal, "Completed")
        self.setHeaderData(STATUS, Qt.Horizontal, "Status")
        self.setHeaderData(DT_ARCHIVED, Qt.Horizontal, "Archived")
        self.setHeaderData(PRIORITY_ID, Qt.Horizontal, "Task ID")
        self.set_filters(perspective, category)
        if not perspective:
            self.setSort(DT_ADDED, Qt.DescendingOrder)
        elif perspective == 'Completed':
            self.setSort(DT_COMPLETE, Qt.DescendingOrder)
        else:
            self.setSort(WEIGHT, Qt.DescendingOrder)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()
        self.dialog = Dialogs()
        self.status = None

    def data(self, index, role):
        """ Returns the data stored under the given role
                for the item referred to by the index. """
        value = super(PriorityModel, self).data(index, role)
        if role == Qt.TextColorRole and index.column() == WEIGHT:
            return QColor(Qt.blue)
        if role == Qt.DisplayRole and index.column() in [DT_ADDED, DT_COMPLETE, DT_ARCHIVED]:
            return value.date().toString('yyyy-MM-dd')
        if role == Qt.DisplayRole and index.column() == DATE_DUE:
            return value.toString('yyyy-MM-dd')
        return value

    def set_filters(self, perspective, category):
        log.debug("set_filters():")  # consider: for key_val in filters: if(/get)
        if perspective == 'Active':
            if category:
                self.setFilter("STATUS IN ('%s','Overdue') AND CATEGORY = '%s'" % (perspective, category))
            else:
                self.setFilter("STATUS IN ('%s','Overdue')" % perspective)
        elif perspective:
            if category:
                self.setFilter("STATUS = '%s' AND CATEGORY = '%s'" % (perspective, category))
            else:
                self.setFilter("STATUS = '%s'" % perspective)
        elif category:
            self.setFilter("CATEGORY = '%s'" % category)
        self.refresh()

    def refresh(self):
        log.debug("refresh()")
        self.select()

    def add_priority(self, task, weight, category, description, importance, urgency, difficulty, date_due):
        """ Add record from input group box """
        log.debug("add_priority()")
        self.database().transaction()
        query = QSqlQuery()
        query.prepare("INSERT INTO priority "
                      "(TASK, WEIGHT, CATEGORY_ID, DESCRIPTION, IMPORTANCE, URGENCY, DIFFICULTY, DATE_DUE) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
        query.addBindValue(task)
        query.addBindValue(weight)
        query.addBindValue(category)
        query.addBindValue(description)
        query.addBindValue(importance)
        query.addBindValue(urgency)
        query.addBindValue(difficulty)
        query.addBindValue(date_due)
        if not query.exec_():
            error_text = query.lastError().text()
            self.dialog.db_error("INSERT FAILED", error_text)
        else:
            self.database().commit()
            self.status = "\nSuccess. '%s' Added to DB.\n" % task
        self.refresh()

    def update_priority(self, task, weight, category, description, importance, urgency, difficulty, date_due, update_id):
        """ Update record from input group box """
        # todo: check for "completed" argument to route as update/archive/delete
        log.debug("update_priority()")
        self.database().transaction()
        query = QSqlQuery()
        query.prepare("UPDATE priority "
                      "SET TASK = ?, WEIGHT = ?, CATEGORY_ID = ?, DESCRIPTION = ?, "
                      "IMPORTANCE = ?, URGENCY = ?, DIFFICULTY = ?, DATE_DUE = ? "
                      "WHERE PRIORITY_ID = ?")
        query.addBindValue(task)
        query.addBindValue(weight)
        query.addBindValue(category)
        query.addBindValue(description)
        query.addBindValue(importance)
        query.addBindValue(urgency)
        query.addBindValue(difficulty)
        query.addBindValue(date_due)
        query.addBindValue(update_id)
        if not query.exec_():
            error_text = query.lastError().text()
            self.dialog.db_error("UPDATE FAILED", error_text)
        else:
            self.database().commit()
            self.status = "\nSuccess. Updated Priority ID %s.\n" % update_id
        self.refresh()

    def priority_action(self, priority_id, action):
        log.debug("%s" % action.upper())
        db_arg = int(db_actions.get(action, None))
        if db_arg and not db_arg == 5:
            self.database().transaction()
            query = QSqlQuery()
            query.prepare("UPDATE priority SET STATUS_ID = ? WHERE PRIORITY_ID = ?")
            query.addBindValue(db_arg)
            query.addBindValue(priority_id)
            if not query.exec_():
                error_text = query.lastError().text()
                self.dialog.db_error("%s FAILED" % action.upper(), error_text)
            else:
                self.database().commit()
                self.status = "\t%s Success: Priority ID %s.\n" % (action, priority_id)
            # self.refresh()
        elif db_arg == 5:
            self.database().transaction()
            query = QSqlQuery()
            query.prepare("DELETE FROM priority WHERE PRIORITY_ID = ?")
            query.addBindValue(priority_id)
            if not query.exec_():
                error_text = query.lastError().text()
                self.dialog.db_error("%s FAILED" % action.upper(), error_text)
            else:
                self.database().commit()
                self.status = "\t%s Success: Priority ID %s.\n" % (action, priority_id)
        else:
            self.status = "\tDB_model.priority_action() failed: '%s' not recognized.\n" % action
        self.refresh()

    def search(self, task="", category="", completed="", year=""):
        """search all priorities"""
        # self.cur.execute("SELECT * FROM book WHERE title=? OR author=? OR year=? OR isbn=?", (title,author,year,isbn))
        # rows=self.cur.fetchall()
        # return rows
        pass


class DetailModel(QSqlRelationalTableModel):
    def __init__(self, priority_filter):
        super(DetailModel, self).__init__()
        self.setTable('priority')
        self.setHeaderData(DT_ADDED, Qt.Horizontal, "Date Added")
        self.setHeaderData(DESCRIPTION, Qt.Horizontal, "Description")
        self.setHeaderData(DESCRIPTION, Qt.Horizontal, Qt.AlignJustify, Qt.TextAlignmentRole)
        if priority_filter != '-1':
            self.setFilter("Priority_ID = %s" % priority_filter)
        self.select()


class DBInterface:
    def __init__(self, db_args, **kwargs):
        """ db_args - for db connection and sp call
                See db_cnx setter below """
        self.dialog = Dialogs()
        self._db = QSqlDatabase.addDatabase('QMYSQL')
        self.db_cnx = db_args
        self.db_args = db_args

    def call_process(self, sp_arg=None):
        """ update urgent priorities' weight in db (by date) """
        query = QSqlQuery()
        procedure = "%s.%s" % (self.db_args['db'], self.db_args['sp'])

        if sp_arg:
            call_statement = "CALL %s ('%s')" % (procedure, sp_arg)
        else:
            call_statement = "CALL %s" % procedure

        if not query.exec_(call_statement):
            log.debug("SP CALL FAILED: %s" % query.lastError().text())

        return QSql.Out

    def sql_do(self, sql, params = ()):
        """
            db.sql_do( sql[, params] )
            method for non-select queries
                sql is string containing SQL
                params is list containing parameters
            returns nothing
        """
        self._db.execute(sql, params)
        self._db.commit()

    def sql_query(self, sql):
        """ db.sql_query(sql[, params]) --> generator method for queries
                sql is string containing SQL; params is list containing parameters
            Returns a generator with one row per iteration-->each row is Row factory """
        query = QSqlQuery()
        query.exec_(sql)  # query.exec_(sql, params)
        while query.next():
            yield query.value(0), query.value(1)
        # formerly:
        # def sql_query(self, sql, params = ()):
        #     c = self._db.cursor()
        #     c.execute(sql, params)
        #     for r in c:
        #         yield r

    def sql_query_row(self, sql, params = ()):
        """
            db.sql_query_row( sql[, params] )
            query for a single row
                sql is string containing SQL
                params is list containing parameters
            returns a single row as a Row factory
        """
        c = self._db.cursor()
        c.execute(sql, params)
        return c.fetchone()

    def sql_query_value(self, sql, params = ()):
        """
            db.sql_query_row( sql[, params] )
            query for a single value
                sql is string containing SQL
                params is list containing parameters
            returns a single value
        """
        log.debug("sql_query_value(sql):\n\t%s" % sql)
        query = QSqlQuery()
        if not query.exec_(sql):
            error_text = query.lastError().text()
            self.dialog.db_error("QUERY FAILED:\n\t%s" % error_text)
        while query.next():
            output = query.value(0)
        return output

    def search(self, task="", category_id="", description="", dt_added="", year="",
               date_due="", dt_complete='', status_id="", priority_id=""):
        """search all priorities"""
        query = QSqlQuery()
        query.prepare("SELECT * FROM priority WHERE TASK = ? OR CATEGORY_ID = ? "
                      "OR DESCRIPTION = ? OR DT_ADDED = ? OR DATE_DUE = ?  "
                      "OR DT_COMPLETE= ?  OR STATUS_ID = ? OR PRIORITY_ID = ?")
        query.addBindValue(task)
        query.addBindValue(category_id)
        query.addBindValue(description)
        query.addBindValue(dt_added)
        query.addBindValue(date_due)
        query.addBindValue(dt_complete)
        query.addBindValue(status_id)
        query.addBindValue(priority_id)

        if not query.exec_():
            log.debug("Search Failed")
            log.debug("DB Error: %s" % query.lastError().text())
            error_text = query.lastError().text()
            self.dialog.db_error("Search Failed", error_text)
        while query.next():
            return query.value()

    def getrec(self, id):
        """
            db.getrec(id)
            get a single row, by id
        """
        query = 'SELECT * FROM {} WHERE id = ?'.format(self.table)
        c = self._db.execute(query, (id,))
        return c.fetchone()

    def getrecs(self):
        """
            db.getrecs(id)
            get all rows, returns a generator of Row factories
        """
        query = 'SELECT * FROM {}'.format(self.table)
        c = self._db.execute(query)
        for r in c:
            yield r

    def insert(self, rec):
        """
            db.insert(rec)
            insert a single record into the table
                rec is a dict with key/value pairs corresponding to table schema
            omit id column to let SQLite generate it
        """
        klist = sorted(rec.keys())
        values = [rec[v] for v in klist]  # a list of values ordered by key
        q = 'INSERT INTO {} ({}) VALUES ({})'.format(
            self.table,
            ', '.join(klist),
            ', '.join('?' for i in range(len(values)))
        )
        c = self._db.execute(q, values)
        self._db.commit()
        return c.lastrowid

    def update(self, id, rec):
        """
            db.update(id, rec)
            update a row in the table
                id is the value of the id column for the row to be updated
                rec is a dict with key/value pairs corresponding to table schema
        """
        klist = sorted(rec.keys())
        values = [rec[v] for v in klist]  # a list of values ordered by key

        for i, k in enumerate(klist):       # don't update id
            if k == 'id':
                del klist[i]
                del values[i]

        q = 'UPDATE {} SET {} WHERE id = ?'.format(
            self.table,
            ',  '.join(map(lambda str: '{} = ?'.format(str), klist))
        )
        self._db.execute(q, values + [ id ])
        self._db.commit()

    def delete(self, id):
        """
            db.delete(id)
            delete a row from the table, by id
        """
        query = 'DELETE FROM {} WHERE id = ?'.format(self.table)
        self._db.execute(query, [id])
        self._db.commit()

    def countrecs(self, table, params):
        """
            db.countrecs()
            count the records in the table
            returns a single integer value
        """
        log.debug("count-recs(table, params):\n\t%s WHERE %s" % (table, params))
        query = QSqlQuery()
        query.prepare("SELECT COUNT(*) FROM ? WHERE ?")
        query.addBindValue(table)
        query.addBindValue(params)
        if not query.exec_():
            error_text = query.lastError().text()
            self.dialog.db_error("QUERY FAILED:\n\t%s" % error_text)
        while query.next():
            return query.value(0)

    ### db_cnx property
    @property
    def db_cnx(self):
        return

    @db_cnx.setter
    def db_cnx(self, db_args):
            self._db.setHostName(db_args['host'])
            self._db.setPort(int(db_args['port']))
            self._db.setDatabaseName(db_args['db'])
            self._db.setUserName(db_args['user'])
            self._db.setPassword(db_args['pw'])

            if not self._db.open():
                self.dialog.db_error('Database Error', self._db.lastError().text())
                log.warning("Database Error: %s" % self._db.lastError().text())
            else:
                log.debug("Connection success")

    @db_cnx.deleter
    def db_cnx(self):
        self._db.close()
