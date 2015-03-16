# -*- coding: utf-8 -*-
from __future__ import absolute_import
import cx_Oracle


class AddressService(object):
    def __init__(self, user, password, sid, host='localhost', port=1521):
        dsn = cx_Oracle.makedsn(host, port, sid)
        self.conn = cx_Oracle.connect(user, password, dsn)
        self.cursor = self.conn.cursor()
        self.cursor.prepare("""
            SELECT first_name, last_name, email
            FROM library_person_lookup
            WHERE mit_id=:mit_id""")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.conn.close()

    def lookup(self, id):
        res = self.cursor.execute(None, {'mit_id': id}).fetchone()
        return res
