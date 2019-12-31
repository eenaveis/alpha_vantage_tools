"""
Example scripts from the 'docs/quickstart_guide.md'.

"""

def download_csv():
	from alpha_vantage_tools.av_funcs import LoadAlphaVantage

	av = LoadAlphaVantage()
	my_data = av.alpha_vantage("KO", write_csv = True) # (my_data == [])

def download_multiple_csv_files():
	from alpha_vantage_tools.av_funcs import LoadAlphaVantage

	symbols = ["PG", "JNJ", "KO"]
	av = LoadAlphaVantage()
	my_data = av.load_csv(symbols)

def store_mixed_data():
	from alpha_vantage_tools.av_funcs import LoadAlphaVantage
	from alpha_vantage_tools.db_funcs import SQLiteDB

	symbols = ["PG"] # can be passed as a string also
	av = LoadAlphaVantage()
	db = SQLiteDB("mixed.db")

	daily_adjusted = av.load_symbols(symbols, av_fun = "TIME_SERIES_DAILY_ADJUSTED")
	intraday_data = av.load_symbols(symbols, av_fun = "TIME_SERIES_INTRADAY", interval = "60min")
	monthly_data = av.load_symbols(symbols, av_fun = "TIME_SERIES_MONTHLY")

	db.insert_dict(daily_adjusted)
	db.insert_dict(intraday_data)
	db.insert_dict(monthly_data)

if __name__ == '__main__':
	pass