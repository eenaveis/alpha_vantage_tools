import sqlite3
import os
from .config import db_queries
from .helpers import read_csv, header_row
import re

class SQLiteConn(object):
    """
    Database connection object.

    """
    def __init__(self, db):
        self.db = db
        self.conn = None
        self.flag = "connection closed"
    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.flag = "connected"
        return self.conn
    def __exit__(self, type, value, traceback):
        if(traceback == None):
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        self.flag = "connection closed"

class SQLiteDB(object):
    """
    SQLite interface.

    """
    defaults = db_queries()

    def __init__(self, db, create = True):
        """
        Pass database path as str. New SQLite database is created by default if 
        an existing database is not found.
        
        """
        self.db = db
        if(not os.path.isfile(db) and create):
            self.create(db)

    @staticmethod
    def with_open_db(db, fun, *args, **kwargs):
        """
        Context manager for database connections.

        """
        with SQLiteConn(db) as conn:
            result = fun(conn, *args, **kwargs)
        return result

    @staticmethod
    def execute_query(db, query, data = None, fetch = False):
        """
        Execute SQL query. Returns the query result.
        
        """

        def wrapper(conn, query, data = None, fetch = False): 
            c = conn.cursor()      
            try:
                if(data):
                    c.execute(query, data)
                elif (fetch):
                    return c.execute(query).fetchall()
                else: 
                    return c.execute(query)
            except(
                sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.DatabaseError) as e:
                print("Error: {0}".format(e))

        return SQLiteDB.with_open_db(db, wrapper, query, data, fetch)

    @staticmethod
    def create(db, table = "stocks"):
        """
        Create new database/table for stock price data.

        """
        query_columns = SQLiteDB.defaults["columns_adjusted"]
        query = SQLiteDB.defaults["create_table"].format(table = table, columns = query_columns)

        SQLiteDB.execute_query(db, query)

    def insert_row(self, row, table = "stocks"):
        """
        Insert row.

        Pass the inserted row as a one-dimensional Python list.

        """

        if(header_row(row)):
            return

        row = row[:]
        if(len(row) < 12):
            row.insert(8, None)
            row.extend((None, None))

        query_columns = "({}?);".format("?, " * 11)
        query = " ".join([self.defaults["insert"], query_columns]).format(table = table)
        self.execute_query(self.db, query, data = row)

    def insert_timeseries(self, data, table = "stocks"):
        """
        Insert multiple rows of stock data into sqlite database.

        Pass data as a two-dimensional Python list.

        """ 
        for row in data:
            self.insert_row(row, table)
 
    def insert_csv(self, directory = ".", select = "all", table = "stocks"):
        """
        Insert csv files to SQLite database.

        Arguments:
        directory -- Source directory. (Default == current directory)
        select -- Pass 'all' or a list of files. (default == 'all')
        table -- SQLite table name. (default == 'stocks')

        """
        results = []
        def insert_row(i, row):
            self.insert_row(row, table = table)

        # handle selection
        if select == "all":
            file_list = [ file for file in os.listdir(directory)]
        else:
            file_list = select if isinstance(select, list) else [select]
            
        # go trough each file and insert rows into the database
        for file in file_list:
            file_path = "/".join([directory, file])
            results.append(read_csv(file_path, fun = insert_row))
        
    def insert_dict(self, data, table = "stocks"):
        """
        Insert a dictionary containing stock price data into SQLite.

        """
        for stock in data.keys():
            for row in data[stock]:
                self.insert_row(row, table = table)
    
    def __select_top(self, table = "stocks", n = 10, direction = "ASC"):
        """
        Print the top/bottom n rows of a database table.

        Columns are suppressed to fit better on screen.

        """
        query_result = self.execute_query(
            self.db, self.defaults["select_top"].format(table = table, direction = direction, n = n), 
            fetch = True)
        header_row = "timestamp, symbol, interval, ... ..., close, volume".split(",")

        print(("|{:>10.10}" * len(header_row)).format(*header_row))
        for row in query_result:
            row = list(row[:2]) + [row[3]] + ["... ..."] + [row[7]] + [row[9]]
            n_cols = len(row)
            print(("|{:>10.10}" * n_cols).format(*map(str, row)))
    
    def head(self, table = "stocks", n = 10):
        """
        Prints first n rows of a database table.

        """
        self.__select_top(table, n, direction = "ASC")

    def tail(self, table = "stocks", n = 10):
        """
        Print last n rows of a database table.

        """
        self.__select_top(table, n, direction = "DESC")