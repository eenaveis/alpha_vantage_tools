# alpha_vantage_tools
Tools for gathering and storing stock price data from the Alpha Vantage API

## About
Copyright (c) 2019, Emil Sievänen

This repository contains some useful tools for downloading and storing stock price data from the Alpha Vantage API. Stock price data can be downloaded as separate csv files or stored as a python dictionary, and inserted into a SQLite database. You can use alpha_vantage_tools free of charge and it is licensed under the *MIT license*. See full license and terms of use in the "LICENSE" file.

**IMPORTANT!**

   This project is currently under development stage and some of the functions in the module might not be fully stable.

   The `db_create` function is assumed to be used with the other functions in the module. Otherwise you might encounter problems with duplicate values when updating your stock data.

   Support for "Stock Time Series" API functions only (except "TIME_SERIES_INTRADAY"). See [Alpha Vantage API documentation](https://www.alphavantage.co/documentation/) for more information.


## Contents

[Quick-Start](#quick-start)

[Requirements](#requirements)

[Installation](#installation)

[Usage](#usage)


## Quick-Start

**STEP 1:** download and install the module from command line. Create an environment variable file to current working directory for accessing your API key.
```
git clone https://github.com/eenaveis/alpha_vantage_tools
pip install -e <path-to-alpha-vantage>

echo 'SECRET_KEY="YOUR_API_KEY"' > .env
```

**STEP 2:** import the module and load your API key from the created '.env' file.
```python
import alpha_vantage_tools as av

api_key = av.get_env()
```

**STEP 3:** get the latest 100 daily datapoints for Amazon (AMZN) and Google (GOOG).
```python
tickers = ["AMZN", "GOOG"]
my_data = av.load_data(tickers, api_key)
```

**STEP 4:** create a database "test_db.sqlite3" and insert the data stored in the "my_data" python dictionary.
```python
my_db = "stock_db.sqlite3"

# table 'stocks' is created by default
av.db_create(my_db)

av.db_insert(my_db, "stocks", my_data)

# Print the first 10 rows of the table.
av.db_head(my_db)
# Print the last 10 rows of the table.
av.db_tail(my_db)
```

**Thats it!** Now you have some well organized stock data for back-testing your trading strategies.

## Requirements
  * [Python3](https://www.python.org/downloads/)
  * [python-dotenv](https://github.com/theskumar/python-dotenv)
  * [setuptools](https://github.com/pypa/setuptools) (for installation)

## Installation

Install `python-dotenv` via `pip install -U python-dotenv`

`setuptools` should be already installed by default on Python3.

You can install the `alpha_vantage_tools` locally, by first cloning or downloading the repository and installing the package from command line `pip install -e <path-to-alpha-vantage>`. The option `-e` is optional, but this way you can modify the package contents on your local machine.

Alternatively you can use it without using `pip install` inside python interpreter (or script). Notice, that you must navigate to the package directory (containing the 'setup.py' file) when using without installation.

## Usage
After succesfully installing the package and dependencies, you can import it like any python module via `import alpha_vantage_tools`.

For convenience, you can create an environment variable file to store your API key. Create the file from command line `echo 'SECRET_KEY="YOUR_API_KEY"' > .env` or use your favorite text editor.

### Functions

*Alpha Vantage API:*

`read_symbols`
  Read a text file containing ticker symbols. Returns a python list.

`load_data`
  Load data into a python dictionary. Ignores all corrupted files.

`load_csv`
  Similar to the load_data, but downloads the data as separate csv files.


*SQLite API:*

`db_create`
  Create a database for storing stock data.

  Database schema: 
  stocks(PK(date, symbol), open, high, low, close, adjusted_close*, volume, dividend_amount*, split_coeff*
  (* only for dividend/split adjusted data)

`db_insert_csv`
  Insert stock data from csv file(s) into SQLite.

`db_insert_dict`
  Insert stock data from python dictionary into SQLite.

`db_head`
  Print the first 10 rows of a SQLite database table.

`db_tail`
  Print the last 10 rows of a SQLite database table.


*Helper functions:*

`get_env()`
  Load environment variable file. Returns the API key stored in the '.env' file.