# -*- coding: utf-8 -*-
import sqlite3
import os.path
from . import config
from . import logger


class DbHandler:
    def __init__(self, filename=None, initscript=None):
        if not filename:
            self.filename = config['dbfilename']
        else:
            self.filename = filename
        if not initscript:
            self.initscript = config['dbinitscript']
        else:
            self.initscript = initscript
        if not os.path.isfile(self.initscript):
            logger.critical('Cannot find database initialization script')
        if not os.path.isfile(self.filename):
            logger.warning('Database file wasnt found. Creating the new one')
            self.conn = sqlite3.connect(self.filename)
            c = self.conn.cursor()
            with open(self.initscript, encoding='utf-8') as fh:
                    c.executescript(fh.read())
            self.conn.commit()
        else:
            self.conn = sqlite3.connect(self.filename)

    def q(self, query, *args):
        c = self.conn.cursor()
        logger.debug('Executing SQL-query: {0}'.format(query))
        c.execute(query, *args)
        self.conn.commit()
        return c.fetchall()
