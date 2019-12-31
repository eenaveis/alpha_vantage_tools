import unittest
import sys
import json
from alpha_vantage_tools.av_funcs import LoadAlphaVantage
import random
from unittest.mock import patch, call
from os.path import isfile
from os import remove
from alpha_vantage_tools.config import api_parameters
from alpha_vantage_tools.helpers import get_env
from .helpers import basic_test_data, create_test_csv_generic

# Load testing data
test_data = basic_test_data()
symbol = random.choice(test_data["symbols"])
av = LoadAlphaVantage()
# Path
load_av_path = "alpha_vantage_tools.av_funcs.LoadAlphaVantage"

class TestPrivateMethods(unittest.TestCase):
    # convert list items to bytes-like objects
    bytes_response_ok = map(lambda x: x.encode("utf-8"), test_data["response_ok"][0])
    bytes_response_err = [ i[0].encode("utf-8") for i in test_data["response_error"]]

    def test_api_request_returns_response(self):
        resp = av._LoadAlphaVantage__api_request(symbol)
        self.assertTrue(resp != None)

    @patch(load_av_path + "._LoadAlphaVantage__api_request")
    def test_parse_api_request_api_request_called(self, mock_request):
        mock_request.return_value = self.bytes_response_ok
        result = av._LoadAlphaVantage__parse_api_request(symbol)
        mock_request.assert_called_once()

    @patch(load_av_path + "._LoadAlphaVantage__api_request")
    def test_parse_api_request_api_error_raised(self, mock_request):
        mock_request.return_value = self.bytes_response_err
        result = av._LoadAlphaVantage__parse_api_request(symbol)
        self.assertEqual(result, None)

    def test_parse_interval_overnight(self):
        assertions = {  
                        "TIME_SERIES_DAILY" : "daily",
                        "TIME_SERIES_DAILY_ADJUSTED" : "daily",
                        "TIME_SERIES_WEEKLY" : "weekly",
                        "TIME_SERIES_WEEKLY_ADJUSTED" : "weekly",
                        "TIME_SERIES_MONTHLY" : "monthly",
                        "TIME_SERIES_INTRADAY" : None
                    }
        
        for av_fun in api_parameters()["av_fun"]:
            test_row = test_data["test_dict"]["AAPL"][1]
            test_row[3] = None
            av._LoadAlphaVantage__parse_interval_overnight(test_row, av_fun)
            self.assertEqual(test_row[3], assertions[av_fun])

class TestBasicFunctionality(unittest.TestCase):
    @patch(load_av_path + "._LoadAlphaVantage__parse_api_request")
    def test_alpha_vantage_request_called(self, mock_request):
        result = av.alpha_vantage(symbol)
        mock_request.assert_called_once()

    @patch(load_av_path + "._LoadAlphaVantage__parse_api_request")
    def test_alpha_vantage_intraday_request_called_once(self, mock_request):
        av.alpha_vantage(symbol, av_fun = "TIME_SERIES_INTRADAY")
        mock_request.assert_called_once()

    @patch(load_av_path + ".alpha_vantage")
    def test_load_symbols_called_with_and_returns_dict(self, mock_request):
        mock_request.return_value = [[],[]]
        result = av.load_symbols(test_data["symbols"], request_limit = False)
        mock_request.assert_called_with(
            'INTC', av_fun = 'TIME_SERIES_DAILY', interval = None, output = 'compact')
        self.assertIsInstance(result, dict)

    @patch(load_av_path + "._LoadAlphaVantage__parse_api_request")
    def test_alpha_vantage_writes_csv(self, mock_request):
        mock_request.return_value = test_data["test_data"]
        av.alpha_vantage(symbol, write_csv = True)
        self.assertTrue(isfile("./" + symbol + ".csv"))

    @patch(load_av_path + "._LoadAlphaVantage__parse_api_request")
    def test_load_csv_called_and_writes_file(self, mock_request):
        mock_request.return_value = test_data["test_data"]
        av.load_csv("INTC", request_limit = False)
        filename = "INTC" + ".csv"
        self.assertTrue(isfile("./" + filename))
        remove("./" + filename)

    def test_read_symbols_returns_unique(self):
        cols = [["AAPL"],["KO"],["AAPL"],["AAPL"],["PEP"]]
        create_test_csv_generic("test_symbols.csv", cols)
        result = av.read_symbols("test_symbols.csv")
        self.assertEqual(result, {"AAPL", "KO", "PEP"})
        remove("test_symbols.csv")

class TestApiParameters(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_alpha_vantage_parameters(self, mock_request):
        result = {}
        funs = api_parameters()["av_fun"]
        outputs = api_parameters()["output"]
        intervals = api_parameters()["interval"]

        for av_fun in funs:
            if(av_fun != "TIME_SERIES_INTRADAY"):
                interval = None
            else:
                interval = random.choice(list(intervals))
            for output in outputs:
                result[av_fun] = av._LoadAlphaVantage__api_request(
                    symbol, av_fun = av_fun, output = output, interval = interval)

        self.assertEqual(len(result), len(funs))
        self.assertEqual(result.keys(), funs)

    def test_alpha_vantage_bad_argument_output(self):
        with self.assertRaises(AssertionError):
            av.alpha_vantage("TSLA", output = "CYBER_TRUCK")

    def test_alpha_vantage_bad_argument_av_fun(self):
        with self.assertRaises(AssertionError):
            av.alpha_vantage("NOK", av_fun = "NMT_GSM")    
    
    def test_alpha_vantage_bad_argument_interval(self):
        with self.assertRaises(AssertionError):
            av.alpha_vantage(
                "KO", av_fun = "TIME_SERIES_INTRADAY", interval = None)

if __name__ == "__main__":
    unittest.main()










