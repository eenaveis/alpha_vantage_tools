from setuptools import setup

setup(name = 'alpha_vantage_tools',
      version = '0.1.0',
      description = 'Tools for gathering and storing stock price data from the Alpha Vantage API',
      classifiers = [
      	'Development Status :: 3 - Alpha',
      	'Programming Language :: Python 3.6',
      	'License :: MIT',
      	'Topic :: Data Importing :: Database API'
      ],
      keywords = 'alpha vantage, stocks',
      url = 'http://github.com/eenaveis/alpha_vantage_tools',
      author = 'Emil Sievänen',
      license = 'MIT',
      packages = ['alpha_vantage_tools'],
      zip_safe = False)