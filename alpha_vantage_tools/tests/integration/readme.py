from alpha_vantage_tools.av_funcs import LoadAlphaVantage
from alpha_vantage_tools.db_funcs import SQLiteDB

def quickstart():
    """
    README.md 'Quick-start'.

    Returns a tuple of SQLiteDB object and a Python dictionary 'my_data'.

    """
    av = LoadAlphaVantage() # api key loaded in instance variable 'api_key'

    symbols = ["AMZN", "GOOG"]
    my_data = av.load_symbols(symbols)

    db = SQLiteDB("stock_db.sqlite3") # creates new database by default

    db.insert_dict(my_data) # Insert dictionary 'my_data' into the created database

    db.head() # Print the first 10 rows (sorted) of the database table 'stocks'.

    return (db, my_data)

if __name__ == "__main__":
    db, my_data = quickstart()
