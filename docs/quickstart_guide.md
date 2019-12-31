# Quick-start guide

## About
This guide contains all the essentials you need to get started using `alpha_vantage_tools` (>= 0.2.0 only).

## Contents
[Requirements](#requirements)

[Install](#install)

[Usage](#usage)

[SQLite schema](#sqlite-schema)

[Modules](#modules)

[Examples](#examples)

## Requirements
  * [Python3](https://www.python.org/downloads/) (>=3.6.0)
  * [python-dotenv](https://github.com/theskumar/python-dotenv)
  * [setuptools](https://github.com/pypa/setuptools) (for installation)

## Install
Install `alpha_vantage_tools` locally by first cloning the package repository and then running `pip install <local-path>`.

For avoiding typing your api key manually every time, use '.env' file containing your api key and store it in your working directory:
    `echo 'SECRET_KEY="YOUR_API_KEY"' > .env`

## Usage
Three-step algorithm for standard usage is summarized below:
1. Import `av_funcs` and `db_funcs` modules.
2. Create instances of `av_funcs.LoadAlphaVantage` and `db_funcs.SQLiteDB` classes.
3. Download data and insert into SQLite database.

Note that the *latest data point for non-intraday data* is always equal to the *latest full period sample* fetched from the Alpha Vantage API. This is because the actual latest data points are updated in real-time and thus would lead to inconsistency in long-term data storage solutions.

Example scripts can be found in the end of this documentation.

## SQLite schema
The *SQL-query* used in `db_funcs.SQLiteDB.create` that serves as the default database in the package is described below:

```
CREATE TABLE STOCKS (
	(timestamp text, symbol text, timeseries_api text, interval text, open real, 
	high real, low real, close real, adjusted_close real, volume integer, 
	dividend_amount real, split_coeff real), 
PRIMARY KEY (timestamp, symbol, timeseries_api, interval)
);
```

This design enables *"all-in-one"* data storage, so there is no need for creating separate tables for eg. unadjusted and split/dividend adjusted data or for different time-frames. The primary key columns will ensure that no duplicates are inserted in the table.

## Modules
### alpha_vantage_tools.av_funcs.LoadAlphaVantage

`self.__init__(self, api_key = "demo")`

*Create an instance of the LoadAlphaVantage class.*

Sets the 'SECRET_KEY' environment varible (stored in .env file) or the passed 'api_key' argument as the instance variable 'api_key'.

`self.alpha_vantage(
self, symbol, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None, write_csv = False, directory = ".")`

*Pull raw data from the Alpha Vantage API.*

Note: Latest data point == t - 1 for daily, weekly and monthly api.

Arguments:
    
* symbol -- Stock ticker symbol as a character string.   
* av_fun -- Alpha Vantage API function (default == 'TIME_SERIES_DAILY')
* output -- Set 'full' or 'compact': 'full' returns complete price history, 'compact' only latest 100 data points. (default == 'compact')
* interval -- Intraday data time-interval (default == None)
* write_csv -- If set True, download as a csv file. (default == False)
* directory -- Directory for csv file downloads. (default == current directory)
    
Returns a two-dimensional list by default, containing time-series stock price data. If 'write_csv' == True, returns an empty list.

`self.load_symbols(
	self, symbols, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None, request_limit = True)`

*Wrapper for downloading multiple stock time-series.*      

Arguments:
* symbols: Pass multiple ticker symbols as a Python list (or single symbol as str).
* request_limit: Set 5 HTTP requests per minute limit. (default == True)
* See 'LoadAlphaVantage.alpha_vantage' for the remaining keyword arguments.

Returns a dictionary containing the requested data.

`self.load_csv(
	self, symbols, directory = ".", av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None, request_limit = True)`

*Wrapper for multiple csv file downloads.*

Arguments:
* symbols -- Pass multiple ticker symbols as a Python list (or single symbol as str).
* directory -- Set download directory. (default == current directory)
* request_limit -- Set 5 HTTP GET requests per minute limit. (default == True)
* See 'LoadAlphaVantage.alpha_vantage' for the remaining keyword arguments.

`self.read_symbols(path, column_n = 1, skip_rows = 1, sep = ",")`

*Read a column vector containing stock ticker symbols from csv.*

Arguments:
* path -- File path as str.
* column_n -- Select the column number containing ticker symbols. (default == 1)
* skip_rows -- Skip n rows. (default == 1)
* sep -- Set the delimiter value. (default == ",")

Returns a Python set of unique ticker symbols.

### alpha_vantage_tools.db_funcs.SQLiteDB

`self.__init__(self, db, create = True)`

Pass database path as string. *New SQLite database is created by default* if an existing database is not found.

`self.insert_row(self, row, table = "stocks")`

*Insert row into SQLite.*

Pass the inserted row as a one-dimensional list.

`insert_timeseries(self, data, table = "stocks")`

*Insert multiple rows of stock data into SQLite.*

Pass data as a two-dimensional Python list.

`self.insert_dict(self, data, table = "stocks")`

*Insert a dictionary containing stock price data into SQLite.*

`self.insert_csv(self, directory = ".", select = "all", table = "stocks")`

*Insert csv files to SQLite.*

Arguments:
* directory -- Source directory. (Default == current directory)
* select -- Pass 'all' or a list of files. (default == 'all')
* table -- SQLite table name. (default == 'stocks')

`self.head(self, table = "stocks", n = 10)`

*Print first 10 rows (sorted) of a database.*

`self.tail(self, table = "stocks", n = 10)`

*Print last 10 rows (sorted) of a database.*

## Examples

### Download csv or in-memory
```
from alpha_vantage_tools.av_funcs import LoadAlphaVantage

av = LoadAlphaVantage()
my_data = av.alpha_vantage("KO", write_csv = True) # (my_data == [])
```
### Download multiple csv files
```
from alpha_vantage_tools.av_funcs import LoadAlphaVantage

symbols = ["PG", "JNJ", "KO"]
av = LoadAlphaVantage()
my_data = av.load_csv(symbols)
```
### Store mixed data
```
from alpha_vantage_tools.av_funcs import LoadAlphaVantage
from alpha_vantage_tools.db_funcs import SQLiteDB

symbols = ["PG"]
av = LoadAlphaVantage()
db = SQLiteDB("mixed.sqlite3")

daily_adjusted = av.load_symbols(symbols, av_fun = "TIME_SERIES_DAILY_ADJUSTED")
intraday_data = av.load_symbols(symbols, av_fun = "TIME_SERIES_INTRADAY", interval = "60min")
monthly_data = av.load_symbols(symbols, av_fun = "TIME_SERIES_MONTHLY")

db.insert_dict(daily_adjusted)
db.insert_dict(intraday_data)
db.insert_dict(monthly_data)
```