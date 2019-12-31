import sqlite3
import json

def api_parameters():
    """
    Returns a dictionary of supported API parameters (Alpha Vantage).

    """
    params = {

                "av_fun": {
                            "TIME_SERIES_DAILY", 
                            "TIME_SERIES_DAILY_ADJUSTED", 
                            "TIME_SERIES_WEEKLY", 
                            "TIME_SERIES_WEEKLY_ADJUSTED", 
                            "TIME_SERIES_MONTHLY",
                            "TIME_SERIES_INTRADAY"
                            },

                "output" : {"compact", "full"},

                "interval" : {"1min", "5min", "15min", "30min", "60min"},

                "interval_overnight" : {"daily", "weekly", "monthly"}

            }
    return params

def db_queries():
    """
    Returns a dictionary of default SQL queries.

    """
    queries = {

                "create_table" : """CREATE TABLE {table} ({columns}, 
                                    PRIMARY KEY (timestamp, symbol, timeseries_api, interval));""",
                
                "columns_deprecated" : """date text, symbol text, open real, high real, 
                                          low real, close real, volume integer""",

                "columns_adjusted" : """timestamp text, symbol text, timeseries_api text, interval text, 
                                        open real, high real, low real, close real, 
                                        adjusted_close real, volume integer, 
                                        dividend_amount real, split_coeff real""",

                "insert" : "INSERT INTO {table} VALUES",

                "select_top" : """SELECT * FROM {table} ORDER BY 
                                  symbol {direction}, timestamp {direction} LIMIT {n};"""

                }
    return queries

