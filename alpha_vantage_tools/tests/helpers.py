import json
import csv
from os import path

def basic_test_data():
    """
    Returns a dictionary of basic testing data.
    
    """
    file_path = path.join(path.dirname(__file__), 'fixtures/basic_tests.json')
    with open(file_path, "r") as f:
        test_data = json.load(f)
    return test_data

def create_test_csv(path):
    data = basic_test_data()["test_data"]

    with open(path, "w") as f:
        csv_w = csv.writer(f, delimiter = ",")
        csv_w.writerows(data)

def create_test_csv_generic(path, data):
    with open(path, "w") as f:
        csv_w = csv.writer(f, delimiter = ",")
        csv_w.writerows(data)