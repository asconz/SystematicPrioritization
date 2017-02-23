#! /usr/bin/python
###################
# ConfigParser.py #
###################
import logging
log = logging.getLogger('ConfigParser')


class ParseConfig:
    """ Simple config file support -> main-app passes file for required args """
    _db_args, _table_args, region = {}, {}, []

    def __init__(self, conf_to_parse):
        self.opened_conf_file = open(conf_to_parse, 'rt')
        self.parse(self.opened_conf_file)

    def parse(self, opened_conf_file):
        for line in opened_conf_file.readlines():
            self.parseline(line)

    def parseline(self, line):
        if not self.region:
            if "## db_args ##" not in line:
                return
            else:
                self.region = ['db_args']
        else:
            if "## table_args ##" in line:
                self.region = ['table_args']
                return
            if "=" not in line:
                return
            (conf_line_key, conf_line_value) = line.split('=', 2)
            if self.region == ['db_args']:
                self._db_args[conf_line_key.strip()] = conf_line_value.strip()
            else:
                self._table_args[conf_line_key.strip()] = conf_line_value.strip()

    def db_args(self):
        return self._db_args

    def table_args(self):
        return self._table_args


def test():
    conf_to_parse = sys.argv[1] if len(sys.argv) > 1 else 'PriorityManager.conf'
    try:
        conf = ParseConfig(conf_to_parse)
    except IOError as e:
        print('could not open {},'.format(conf_to_parse), e)
    else:
        db_args, table_args = conf.db_args(), conf.table_args()
        print("DB_args:")
        for k in sorted(db_args):
            print('\t{} is [{}]'.format(k, db_args[k]))
        print("\nTable_args:")
        for k in sorted(table_args):
            print('\t{} is [{}]'.format(k, table_args[k]))

if __name__ == "__main__":
    import sys
    test()


