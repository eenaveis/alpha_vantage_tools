import csv
import os
from time import time
from .helpers import corrupted_data, make_url, api_request_delay, alpha_vantage

def read_symbols(ticker_list, column_n = 1, header = True, sep = ","):
    """
    Read a text file containing stock ticker symbols in a table column.
    """
    try:
        with open(ticker_list, "rt") as csv_file:
            csv_r = csv.reader(csv_file, delimiter = sep)
            counter = -1
            symbols = []
            if header == True:
                for row in csv_r:
                    if counter == -1:
                        counter += 1
                    else:
                        symbols.append(row[column_n - 1].upper())
                        counter += 1
            elif header == False:
                if counter == -1:
                    counter += 1
                for row in csv_r:
                    symbols.append(row[column_n - 1].upper())
                    counter += 1
            else:
                print("Error: Did you mean 'header = True' or 'header = False'?")
                return
            print("{0} ticker symbols!".format(counter))
            return symbols
    except (FileNotFoundError) as e:
        print("Error: {0}".format(e))

 

def load_data(symbols, api_key, av_fun = "TIME_SERIES_DAILY", output = "compact", request_limit = True):
    """
    Download data from the Alpha Vantage API. The downloaded data is stored in the 'stock_data'
    python dictionary.
    """
    # convert API request limit to seconds
    if not request_limit:
        request_delay = 0
    else:
        request_delay = 60 / 5

    # initiate empty dictionaries for stocks and corrupted files
    stock_data = {}
    files_corrupted = []

    # define starting time of the below for loop
    start_time = time()

    print("Estimated downloading time: >{0} seconds...\n".format(request_delay * len(symbols) - request_delay))
    
    for n, symbol in enumerate(symbols):
        print("Downloading {0}/{1}...".format(n + 1, len(symbols)))
        # define starting time of the API request
        start_time_request = time()
        # accept only good data
        data_clean = corrupted_data(symbol, None, api_key, av_fun, output, source = "API")
        if len(data_clean) == 0:
            pass
        else:
            stock_data[symbol] = {"Header": data_clean[0], "Rows": data_clean[1:]}

        # delay next request with respect to the limits
        if n != len(symbols) - 1:
            api_request_delay(start_time_request, request_delay)

    # print statistics
    print("Download complete in {0} seconds!".format(time() - start_time))
    if len(files_corrupted) == 0:
        print("{0} files were downloaded".format(len(symbols)))
    else:
        print("{0} / {1} corrupted files were ignored".format(len(files_corrupted), len(symbols)))
    return stock_data

def load_csv(symbols, api_key, av_fun = "TIME_SERIES_DAILY", output = "compact", request_limit = 5, path = os.curdir):
    """
    A wrapper function for 'load_data' to download csv files.
    """
    # current directory
    work_directory = os.getcwd()
    
    # change to an existing directory or create a new one
    try:
        os.chdir(path)
    except FileNotFoundError:        
        print("Directory '{0}' not found...".format(path))
        print("Creating new directory '{0}' in the current working directory...".format(path))
        os.mkdir(path)
        os.chdir(path)

    # Download stock data
    data_clean = load_data(symbols, api_key, av_fun, output, request_limit)

    # write csv file
    for symbol in symbols:
        with open("{0}.csv".format(symbol), "wt") as text_file:
            csv_w = csv.writer(text_file, delimiter = ",")
            csv_w.writerow(data_clean[symbol]["Header"])
            for row in data_clean[symbol]["Rows"]:
                csv_w.writerow(row)

    # change back to the original work_directory
    os.chdir(work_directory)