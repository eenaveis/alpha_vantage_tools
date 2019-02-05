from dotenv import load_dotenv
from os import getenv
import csv
import sqlite3
from time import time, strptime, sleep
from urllib.request import urlopen
from urllib.error import HTTPError

# empty list for corrupted files
files_corrupted = []

def get_env():
    """
    Returns the API key from the environment variable file.
    """
    load_dotenv()
    api_key = getenv("SECRET_KEY")
    return api_key

def parameters():
    """
    Returns a dictionary of default parameters.
    """

    defaults = {"sqlite_extension": [".db", ".db3", ".sqlite", ".sqlite3"],
                "api_fun": ["TIME_SERIES_DAILY", "TIME_SERIES_DAILY_ADJUSTED", "TIME_SERIES_WEEKLY",
                "TIME_SERIES_WEEKLY_ADJUSTED", "TIME_SERIES_MONTHLY"],
                }
    return defaults 

def db_file_extension(file):
    """
    Returns boolean value.
    """
    file_extensions = parameters()["sqlite_extension"]
    for extension in file_extensions:
        if file.endswith(extension):
            return True
    return False

def alpha_vantage(symbol, api_key, av_fun = "TIME_SERIES_DAILY", output = "compact"):
    """
    Pull raw data from the Alpha Vantage API.

    Returns a list of rows containing time-series stock price data.
    """
    try:
        temp = []
        url = make_url(symbol, api_key, av_fun, output)
        resp = urlopen(url)
        split_newline = resp.read().decode("utf-8").split("\n")
        # parse the raw data separated by comma
        csv_r = csv.reader(split_newline, delimiter = ",")
        for row in csv_r:
            temp.append(row)
        # check if the last row is empty
        if temp[-1] == []:
            temp = temp[:-1]
    except HTTPError as e:
        print("Error: {0}. Parameter values might contain typing errors".format(e))
        
    return temp 

def corrupted_data(symbol, dictionary = None, api_key = "demo", av_fun = "TIME_SERIES_DAILY", output = 'compact', source = "API"):
    """
    Helper function for verifying data quality.

    Returns an empty list if data is corrupted, otherwise a list of rows is returned.
    """

    # get data
    if source == "API":
        data = alpha_vantage(symbol, api_key, av_fun, output = output)
    elif source == "dict":
        data = [dictionary[symbol]["Header"]] + dictionary[symbol]["Rows"]
    elif source == "csv":
        data = []
        with open("{0}.csv".format(symbol), "rt") as csv_file:
            csv_r = csv.reader(csv_file, delimiter = ",")
            for row in csv_r:
                data.append(row)
    else:
        print("Error: invalid 'source' parameter")

    # empty list for good data
    rows = []
    # check for corrupted data
    for n, row in enumerate(data):
        if n == 0 and (len(row) == 6 or len(row) == 9):
            rows.append(row)
        else:
            try:
                strptime(row[0], "%Y-%m-%d")
                float(row[1]) 
                float(row[2]) 
                float(row[3]) 
                float(row[4])
                if len(row) == 9:
                    float(row[5])
                    int(row[6])
                    float(row[7])
                    float(row[8])
                else:
                    int(row[5])
                rows.append(row)
            except ValueError as e:
                print("Error: {0}".format(e))
                print("Ignoring corrupted file {0}".format(symbol))
                rows = []
                break

    return rows

def make_url(symbol, api_key, av_fun = "TIME_SERIES_DAILY", output = "compact"):
    """
    Helper function for API requests.

    Returns an url with the given arguments.
    """
    try:
        url = "https://www.alphavantage.co/query?function={0}&symbol={1}&outputsize={2}&apikey={3}&datatype=csv".format(av_fun, symbol, output, api_key)
        
        return url
    except NameError as e:
        print("Error: {0}".format(e))

def api_request_delay(start_time, request_delay):
    """
    Helper function for delaying API requests.
    """
    delta_time = time() - start_time
    if delta_time >= request_delay:
        print("Download time {} seconds".format(delta_time))
    else:
        print("download time {} seconds".format(delta_time))
        print("Starting next download...")
        sleep(request_delay - delta_time)

def insert_to_sql(data, symbol, connection, cursor, table):
    """
    Insert stock data to sqlite database.
    """
    total_rows = 0
    error_message = False
    counter = -1
    for row in data:
        temp = row[:]
        # skip first row
        if counter == -1:
            counter += 1
        else:
            try:
                temp.insert(1, symbol)
                if len(temp) == 7:
                    cursor.execute("INSERT INTO {0} VALUES (?, ?, ?, ?, ?, ?, ?);".format(table), temp)
                    counter += 1
                if len(temp) == 10:
                    cursor.execute("INSERT INTO {0} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);".format(table), temp)
                    counter += 1
            except sqlite3.IntegrityError:
                error_message = True
                continue
    connection.commit()
    if error_message:
        print("Some (duplicate) rows for symbol '{0}' were not inserted into the table '{1}'".format(symbol, table))
    total_rows += counter

def db_head(db, table = "stocks"):
    """
    Print the first 10 rows of a database table.
    """
    conn, c = db_connect(db)
    c.execute("SELECT * FROM {0} ORDER BY date DESC LIMIT 10;".format(table))
    for row in c:
        print(row)

def db_tail(db, table = "stocks"):
    """
    Print the last 10 rows of a database table.
    """
    conn, c = db_connect(db)
    c.execute("SELECT * FROM {0} ORDER BY date DESC LIMIT 10;".format(table))
    for row in c:
        print(row)