# -*- coding: utf-8 -*-
"""
this module provides a dict that persists it's keys/values to an sqlite3 db.
Author: matthewb...@gmail.com

Timo Petmanson:
- added manual commit feature for bulk inserts.

"""

import sqlite3 as db
import cPickle as pickle
from UserDict import DictMixin

__all__ = ['PersistentDict']

class PersistentDict(DictMixin, object):
    """stores and retrieves persistent data through a dict-like interface"""
    
    def __init__(self, *args, **kwargs):
        """
        initialize a new PersistentDict with the specified db file.
        """
        self.__conn = db.connect(*args, **kwargs)
        self.__conn.text_factory = str
        sql = """
        CREATE TABLE IF NOT EXISTS config (
            key TEXT NOT NULL PRIMARY KEY UNIQUE,
            value BLOB
        );
        """
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(sql)
        self.__conn.commit()
        self.__autocommit = True

    def autocommit(self, value=None):
        """Should we automatically commit after each insert/update/delete?"""
        if value == None:
            return self.__autocommit
        else:
            self.__autocommit = bool(value)

    def __serialize(self, value):
        """convert object to a string to save in the db"""
        return pickle.dumps(value)
    
    def __deserialize(self, value):
        """convert a string into an object"""
        return pickle.loads(value)
    
    def __key_exists(self, key):
        """check the database to see if a key exists"""
        self.__cursor.execute(
            "SELECT COUNT(key) FROM config WHERE key=?;", (key,))
        count = int(self.__cursor.fetchone()[0])
        if count:
            return True
        else:
            return False
            
    def __getitem__(self, key):
        """return the value of the specified key"""
        if not self.__key_exists(key):
            raise KeyError()
        val = None
        self.__cursor.execute("SELECT value FROM config WHERE key=?;", (key,))
        row = self.__cursor.fetchone()
        if row and len(row) > 0:
            val = self.__deserialize(row[0])
        return val
    
    def __setitem__(self, key, value):
        """set the value of the specified key"""
        if self.__key_exists(key):
            self.__cursor.execute(
                "UPDATE config SET value=? WHERE key=?;", 
                (self.__serialize(value), key))
            if self.__autocommit:
                self.__conn.commit()
        else:
            self.__cursor.execute(
            "INSERT INTO config (key,value) VALUES(?,?);",
                (key, self.__serialize(value)))
            if self.__autocommit:
                self.__conn.commit()
        
    def __delitem__(self, key):
        """remove the specifed value from the database"""
        if not self.__key_exists(key):
            raise KeyError()
        self.__cursor.execute("DELETE FROM config WHERE key=?;", (key,))
        if self.autocommit:
            self.__conn.commit()
    
    def keys(self):
        """returns a list containing each key in the database"""
        keys = []
        self.__cursor.execute("SELECT key FROM config;")
        for rows in self.__cursor:
            keys.append(rows[0])
        return set(keys)

    def commit(self):
        """Commit all changes. Not necessary when __autocommit == True."""
        self.__conn.commit()

    def close(self):
        self.__conn.commit()
        self.__conn.close()


