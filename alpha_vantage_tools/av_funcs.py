import csv
import os
import re
from time import time, sleep
from datetime import timedelta
from urllib.request import urlopen
from urllib.error import HTTPError
from .helpers import write_csv as write_csv_
from .helpers import read_csv, get_env
from .config import api_parameters

class LoadAlphaVantage(object):
    """
    Alpha Vantage API wrapper class.

    """
    def __init__(self, api_key = "demo"):
            self.api_key = get_env() or api_key

    def __make_url(
        self, symbol, api_key, av_fun = "TIME_SERIES_DAILY", output = "compact", 
        interval = None):
        """
        Create url string for api requests.
        
        """
        try:
            base_url = "https://www.alphavantage.co/query?"
            params = "function={0}&symbol={1}&outputsize={2}&apikey={3}&datatype=csv"\
            .format(av_fun, symbol, output, api_key)

            if (av_fun == "TIME_SERIES_INTRADAY"):
                return "".join([base_url, params, "&interval={0}".format(interval)])
            
            return base_url + params

        except NameError as e:
            print("Error: {0}".format(e))

    def __api_request_delay(self, start_time, request_delay):
        """
        Delays API requests x seconds.

        """
        delta_time = time() - start_time
        sleep(request_delay - delta_time)

    def __api_request(
        self, symbol, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None):
        """
        Make HTTP GET request to Alpha Vantage API.

        Returns HTTP response object.

        """

        error_msg_ = "Invalid api call with parameter '{param}'."

        assert av_fun in api_parameters()["av_fun"], error_msg_.format(param = "av_fun")
        assert output in api_parameters()["output"], error_msg_.format(param = "output")

        if(av_fun == "TIME_SERIES_INTRADAY"):
            assert interval in api_parameters()["interval"], error_msg_.format(param = "interval")

        try:
            url = self.__make_url(symbol, self.api_key, av_fun, output, interval)
            resp = urlopen(url)
        except HTTPError as e:
            print("Error: {0}.".format(e))
            return

        return resp

    def __parse_api_request(
        self, symbol, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None):
        """
        Parse HTTP response object.

        Returns two-dimensional list or None.

        """

        resp = self.__api_request(symbol, av_fun, output, interval)

        parsed_response = [ line.decode("utf-8").strip("\r\n").split(",") for line in resp]
        
        # Return None if invalid API call.
        if(re.match(r'\s*"([E|e]rror)\s([M|m]essage).*"', parsed_response[1][0]) != None):
            print("Invalid API call for symbol '{0}'".format(symbol))
            return None

        return parsed_response

    def __parse_interval_overnight(self, row, av_fun):
        """
        Parse interval for non-intraday data.

        """
        if(av_fun.startswith("TIME_SERIES_DAILY")):
            row[3] = "daily"
        elif(av_fun.startswith("TIME_SERIES_WEEKLY")):
            row[3] = "weekly"
        elif(av_fun.startswith("TIME_SERIES_MONTHLY")):
            row[3] = "monthly"

    def alpha_vantage(
        self, symbol, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None, 
        write_csv = False, directory = "."):
        """
        Pull raw data from the Alpha Vantage API.

        Note: Latest data point == t - 1 for daily, weekly and monthly api.

        Arguments:
        symbol -- Stock ticker symbol as a character string.
        av_fun -- Alpha Vantage API function (default == 'TIME_SERIES_DAILY')
        output -- Set 'full' or 'compact': 'full' returns complete price history, 
        'compact' only latest 100 data points. (default == 'compact')
        interval -- Intraday data time-interval (default == None)
        write_csv -- If set True, download as a csv file. (default == False)
        directory -- Directory for csv file downloads. (default == current directory)

        Returns a two-dimensional list by default, containing time-series stock price data.
        If 'write_csv' == True, returns an empty list.
        
        """ 
        # Make request and parse response
        parsed_resp = self.__parse_api_request(symbol, av_fun, output, interval)
        # Return None if response == None
        if(parsed_resp == None):
            return None
        # Remove last row if empty
        if(parsed_resp[-1] == []):
            parsed_resp = parsed_resp[:-1]

        # Insert new columns
        for i, row in enumerate(parsed_resp):
            x, y, z = ("symbol", "timeseries_api", "interval") if i == 0 else (symbol, av_fun, interval)
            row.insert(1, z)
            row.insert(1, y)
            row.insert(1, x)
            # parse interval column if necessary
            if(av_fun != "TIME_SERIES_INTRADAY" and i != 0):
                self.__parse_interval_overnight(row, av_fun)

        # Keep only latest datapoint with full period information.
        if(re.search(r"DAILY|MONTHLY|WEEKLY", av_fun)):
            del parsed_resp[1]

        if (write_csv):
            path = "/".join([directory, symbol]) + ".csv"
            write_csv_(path, parsed_resp)
            return []

        return parsed_resp

    def __download(
        self, symbols, request_limit = True, in_memory = True, **kwargs):
        """
        Download interface.

        """
        download_result = {}

        symbols = symbols if isinstance(symbols, list) else [symbols]

        # Download starting time
        start_time = time()

        # counter for errors
        errors = 0
        for i, symbol in enumerate(symbols):

            print("Downloading {0}/{1}...".format(i + 1, len(symbols)), "\r", end = "")
            
            # API request starting time
            start_time_request = time()
            data = self.alpha_vantage(symbol, **kwargs)
            # Keep only good data
            if (data == None):
                errors += 1
            elif(in_memory):
                download_result[symbol] = data
            # delay next request with respect to the limits
            if request_limit and len(symbols) >= 5 and i < len(symbols) - 1:
                self.__api_request_delay(start_time_request, request_delay)

        # print relevant statistics
        print("Download complete in {0}!"\
            .format(timedelta(seconds = time() - start_time)))
        if errors > 0:
            print("{0} / {1} symbols errored.".format(errors, len(symbols)))
        # Return None when writing csv files
        if(not in_memory):
            return
        
        return download_result


    def load_symbols(
        self, symbols, av_fun = "TIME_SERIES_DAILY", output = "compact", interval = None, 
        request_limit = True):
        """
        Wrapper for downloading multiple stock time-series.
        
        Arguments:
        symbols: Pass multiple ticker symbols as a Python list (or single symbol as str).
        request_limit: Set 5 HTTP requests per minute limit. (default == True)
        See 'help(LoadAlphaVantage.alpha_vantage)' for the rest of the keyword arguments.

        Returns a Python dictionary containing the requested data.

        """
        # initialize empty dictionary for stocks
        return self.__download(symbols, request_limit = request_limit, 
        av_fun = av_fun, output = output, interval = interval)

    def load_csv(
        self, symbols, directory = ".", av_fun = "TIME_SERIES_DAILY", output = "compact", 
        interval = None, request_limit = True):
        """
        Wrapper for multiple csv file downloads.

        Arguments:
        symbols -- Pass multiple ticker symbols as a Python list (or single symbol as str).
        directory -- Set destination directory for the downloads. (default == current directory)
        request_limit -- Set 5 HTTP requests per minute limit. (default == True)
        See 'help(LoadAlphaVantage.alpha_vantage)' for other keyword arguments.
        
        """
        self.__download(symbols, request_limit = request_limit, 
            in_memory = False, directory = directory, av_fun = av_fun, 
            output = output, interval = interval, write_csv = True)

    @staticmethod
    def read_symbols(path, column_n = 1, skip_rows = 1, sep = ","):
        """
        Read a column vector containing stock ticker symbols from csv.

        Arguments:
        path -- File path as str.
        column_n -- Select the column number containing ticker symbols. (default == 1)
        skip_rows -- Skip n rows. (default == 1)
        sep -- Set the delimiter value. (default == ",")

        Returns a Python set of unique ticker symbols.

        """
        def filter_fun(i, row, column_n = column_n, skip_rows = skip_rows):
            # Skip header row and select column
            if (i < skip_rows - 1):
                return
            return row[column_n - 1]
        return set(read_csv(path, sep, fun = filter_fun))














