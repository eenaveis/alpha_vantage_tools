# alpha_vantage_tools
Alpha Vantage API wrapper with integrated SQLite interface for easy data ingestion.

## About
Copyright (c) 2019, Emil Sievänen

Development status: alpha

Create convenient data ingestion pipelines for stock market data utilizing the package's Alpha Vantage API wrappers and SQLite interface. You can use alpha_vantage_tools free of charge and it is licensed under the *MIT license*. Full license and terms of use are available in the "LICENSE" file. 

See official [Alpha Vantage homepage](https://www.alphavantage.co/) for more information about the API.

**Version 0.2.0 notes:**
  * New *class-based* implementation
  * Support for TIMESERIES_INTRADAY API
  * Improved "all-in-one" database schema
  * Added basic test suite

## Contents

[Requirements](#requirements)

[Installation](#installation)

[Quick-Start](#quick-start)

## Requirements
  * [Python3](https://www.python.org/downloads/) (>=3.6.0)
  * [python-dotenv](https://github.com/theskumar/python-dotenv)
  * [setuptools](https://github.com/pypa/setuptools) (for installation)

## Installation
To install `alpha_vantage_tools` locally, clone the package repository using `git clone https://github.com/eenaveis/alpha_vantage_tools` and after that `pip install <local-path>`.

## Quick-Start

**STEP 1:** clone and install the package from command line. Create an environment variable file to current working directory for accessing your API key.
```
git clone https://github.com/eenaveis/alpha_vantage_tools
pip install <local-path>

echo 'SECRET_KEY="YOUR_API_KEY"' > .env
```

**STEP 2:** import the module and load your API key from the created '.env' file.
```python
from alpha_vantage_tools.av_funcs import LoadAlphaVantage

av = LoadAlphaVantage() # api key loaded in instance variable "api_key"
```

**STEP 3:** get the latest 100 daily datapoints for Amazon (AMZN) and Google (GOOG).
```python
symbols = ["AMZN", "GOOG"]
my_data = av.load_symbols(symbols)
```

**STEP 4:** create a database "test_db.sqlite3" and insert the data stored in the "my_data" python dictionary.
```python
from alpha_vantage_tools.db_funcs import SQLiteDB

db = SQLiteDB("stock_db.sqlite3") # creates new database by default

db.insert_dict(my_data)

# Print the first 10 rows of the table.
db.head()
```

**Thats it!** Now you have some well organized stock data for back-testing your trading strategies. See 'docs/quickstart_guide.md' for more comprehensive documentation about the package contents.