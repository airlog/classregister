# coding=utf-8

from externals.torndb import Connection as MysqlConnection

class DatabaseManager(MysqlConnection):
    
    def __init__(self, host, user, password, database):
        pass
    
