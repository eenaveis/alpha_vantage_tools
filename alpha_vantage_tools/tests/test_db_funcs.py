import unittest
from unittest.mock import patch
from alpha_vantage_tools.db_funcs import SQLiteConn, SQLiteDB
from .helpers import basic_test_data, create_test_csv_generic
from os import remove, mkdir, chdir
from os.path import isfile
import sqlite3
import json

test_data = basic_test_data()

class TestConn(unittest.TestCase):
	def test_init(self):
		db_connection_object = SQLiteConn("temp.db")
		self.assertEqual(db_connection_object.db, "temp.db")
		self.assertEqual(db_connection_object.conn, None)
	@patch("sqlite3.connect")
	def test_enter_exit_cntx_m(self, mocked_connection):
		db_connection_object = SQLiteConn("temp.db")
		self.assertEqual(db_connection_object.flag, "connection closed")
		with db_connection_object as conn:
			self.assertEqual(db_connection_object.flag, "connected")
			mocked_connection.assert_called_once()
		self.assertEqual(db_connection_object.flag, "connection closed")

class TestDB(unittest.TestCase):
	symbol = "AAPL"
	row = test_data["test_dict"]["AAPL"][1]
	test_dict = test_data["test_dict"]

	@staticmethod
	def basic_insertion(fun_name, *args, **kwargs):
		"""
		wrapper for basic database insertion/assertion.

		Returns SQLiteDB object and query result (SELECT * ...).

		"""
		db = SQLiteDB("temp.db")
		if(fun_name == "insert_row"):
			db.insert_row(*args, **kwargs)
		if(fun_name == "insert_timeseries"):
			db.insert_timeseries(*args, **kwargs)
		if(fun_name == "insert_dict"):
			db.insert_dict(*args, **kwargs)
		if(fun_name == "insert_csv"):
			db.insert_csv(*args, **kwargs)
		query = "SELECT * FROM STOCKS;"
		result = SQLiteDB.execute_query(db.db, query, fetch = True)
		return db, result

	def test_init_db_created(self):
		db = SQLiteDB("temp.db")
		self.assertTrue(isfile("temp.db"))
		remove("temp.db")

	def test_insert_row(self):
		db, result = self.basic_insertion("insert_row", self.row)
		result_ = result[0]
		self.assertEqual(len(result_), 12)
		self.assertEqual(result_[0], self.row[0])
		self.assertEqual(result_[9], self.row[-1])
		self.assertFalse(result_[11] == self.row[-1])
		remove("temp.db")

	def test_insert_duplicate_rows(self):
		db, result = self.basic_insertion("insert_row", self.row)
		db.insert_row(self.row)
		db.insert_row(self.row)
		query = "SELECT * FROM STOCKS;"
		result = SQLiteDB.execute_query(db.db, query, fetch = True)
		self.assertEqual(len(result), 1)
		remove("temp.db")

	def test_insert_timeseries(self):
		db, result = self.basic_insertion("insert_timeseries", self.test_dict["AAPL"])
		self.assertEqual(len(result), 4)
		remove("temp.db")

	def test_insert_dict(self):
		db, result = self.basic_insertion("insert_dict", self.test_dict)
		self.assertEqual(len(result), 8)
		remove("temp.db")

	def test_insert_csv(self):
		create_test_csv_generic("test_csv.csv", self.test_dict["AAPL"])
		db, result = self.basic_insertion("insert_csv", select = "test_csv.csv")
		self.assertTrue(result != [])
		self.assertEqual(len(result), 4)
		remove("temp.db")
		remove("test_csv.csv")
		
if __name__ == '__main__':
	unittest.main()