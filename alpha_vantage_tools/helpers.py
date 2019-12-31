import csv
from os import mkdir, getenv
import os.path
from dotenv import load_dotenv

def get_env():
    """
    Returns API key from the environment variable file.

    """
    load_dotenv()
    api_key = getenv("SECRET_KEY")
    return api_key

def read_csv(path, sep = ",", fun = lambda i, x: x):
    """
    Generic function for reading tabular data. 

    Returns a list of rows. Row values are formatted as strings. 

    """ 
    try:
        with open(path, "rt") as csv_file:
            csv_r = csv.reader(csv_file, delimiter = sep)
            # read and process each row
            result = [ fun(i, row) for i, row in enumerate(csv_r) if fun(i, row) != None]
    except (FileNotFoundError) as e:
        print("Error: {0}".format(e))
        return
    return result

def write_csv(path, data, sep = ","):
    """
    Generic function for writing csv files:

    -Writes csv file in the given path.

    -Creates new directory if non-existing directory given.

    """
    directory = os.path.split(path)[0]

    if(not os.path.isdir(directory)):        
        print("Directory '{0}' not found...".format(directory))
        print("Creating new directory '{0}' in the current directory {1}..."\
            .format(directory, os.getcwd()))
        mkdir(directory)

    try:
        with open(path, "wt") as text_file:
            csv_w = csv.writer(text_file, delimiter = sep)
            csv_w.writerows(data)
    except IsADirectoryError as e:
        print("Error: {0}".format(e))

def header_row(row):
    """
    Check if table row is a header row.

    """

    if(sum([isinstance(col, str) for col in row]) == len(row)):
        try:
            float(row[4])
            return False
        except ValueError:
            return True
    return False
    