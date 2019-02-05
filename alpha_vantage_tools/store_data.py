from .helpers import parameters
import sqlite3
import os
from .helpers import corrupted_data, db_file_extension, insert_to_sql

def db_connect(db):
    """
    Create a database connection.
    Returns sqlite3 connect and cursor objects.
    
    ARGUMENTS:
    db: path to the database as a character string.
    """

    try:
        os.path.isfile(db)
        if db_file_extension(db):
            conn = sqlite3.connect(db)
            c = conn.cursor()
        else:
            print("Error: database file extension must be '.sqlite3'!")
            conn, c = None, None
    except FileNotFoundError:
        print("Error: Database '{0}' does not exist".format(db))
        conn, c = None, None

    return conn, c

def db_create(db = "database.sqlite3", table = "stocks", adjusted_price = False):
    """
    Create new database with one table for stock price data. The table has a total of 7 columns for
    timestamp, symbol, open, high, low, close and volume.
    
    A new table is created if already existing database is found.

    ARGUMENTS: 
    db: path to the database as a character string.
    
    table: name of the table as a character string.
    """
    if db_file_extension(db):
        try:
            conn, c = db_connect(db)
            if adjusted_price:
                c.execute("""CREATE TABLE {0} 
                    ('date' text, symbol text, open real, high real, low real, close real, adjusted_close real,
                        volume integer, dividend_amount real, split_coeff real,
                        PRIMARY KEY(date, symbol));""".format(table))
            elif not adjusted_price:
                c.execute("""CREATE TABLE {0} 
                    ('date' text, symbol text, open real, high real, low real, close real, volume integer,
                        PRIMARY KEY(date, symbol));""".format(table))
            else:
                print("Error: did you mean 'adjusted_price = True'?")
            conn.commit()
            conn.close()
            print("Created new database '{0}'".format(db))
        except sqlite3.OperationalError as e:
            print("Error: {0}".format(e))
    else:
        print("Error: database file extension must be '.sqlite3'!")

def db_insert_csv(db, table, path, select = "all"):
    """
    Insert csv file to SQLite database. The table where the data is imported has to be formatted 
    as in the 'create_stock_db' -function.
    """
    file_list = []

    # check that the database exists and has correct file extension
    if os.path.isfile(db) and db_file_extension(db):
        # create database connection and cursor objects
        conn, c = db_connect(db)

        # select 'all' or user defined list of files
        if select == "all":
            for file in os.listdir(path):
                file_path = path + "/" + file
                if os.path.isfile(file_path):
                    file_list.append(file)

        else:
            if isinstance(select, list):
                file_list = select
            else:
                print("Error: pass 'all' or a python list for argument 'select'")
                return
        
        # go trough each file and insert all rows into the database
        for file in file_list:
            if file.endswith(".csv"):
                symbol = file.split(".")[0]
                file_path = path + "/" + symbol
                data = corrupted_data(file_path, source = "csv")
                if len(data) != 0:
                    insert_to_sql(data, symbol, conn, c, table)
            else:
                print("Error: file '{0}' is not a csv file".format(file))
        
        # close database connection
        conn.close()

    # error messages
    elif not db_file_extension(db):
        print("Error: check database file extension")
    else:
        print("Database '{0}' does not exist".format(db))

def db_insert_dict(db, table, python_dict):
    """
    Insert python dictionary to SQLite database. The table where the data is imported has to be formatted 
    as in the 'create_stock_db' -function.
    """
    conn, c = db_connect(db)
    for stock in python_dict:
        data = corrupted_data(stock, python_dict, source = "dict")
        if len(data) != 0:
            insert_to_sql(data, stock, conn, c, table)
        else:
            pass
    conn.close()
