from setuptools import setup

setup(name = "alpha-vantage-tools",
      version = "0.2.0",
      description = "Alpha Vantage API wrapper with integrated SQLite interface for easy data ingestion.",
      classifiers = [
      	"Development Status :: 3 - Alpha",
      	"Programming Language :: Python 3.6",
      	"License :: MIT",
      	"Topic :: Data Ingestion :: Financial Data"
      ],
      keywords = "alpha vantage, stock markets, database",
      url = "http://github.com/eenaveis/alpha_vantage_tools",
      author = "Emil Sievänen",
      license = "MIT",
      packages = ["alpha_vantage_tools"],
      install_requires = ["python-dotenv"],
      zip_safe = False)