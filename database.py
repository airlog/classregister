# coding=utf-8

import externals
from torndb import Connection as MysqlConnection

class DatabaseManager(MysqlConnection):
    
    def __init__(self, host, user, password, database):
        pass
    
