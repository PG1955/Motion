import os
from os.path import exists
from datetime import datetime, timedelta
import csv

__author__ = "Peter Goodgame"
__name__ = "TempCSV"
__version__ = "v2.1"


class TempCSV:
    """Store Temperature readings over time."""

    def __init__(self):
        self.data = None
        self.columns = ["Timestamp", "Centigrade", "Fahrenheit", "Humidity"]
        self.filename = "temperatures.csv"
        self.refresh_time = datetime.now()
        self.now = datetime.now()
        self.refresh_seconds = 60 * 15
        self.temp_c = None
        self.temp_f = None
        self.humidity = None
        self.exists = os.path.exists(self.filename)
        self.refresh_data(initialise=True)

    def write(self, centigrade, fahrenheit, humidity):
        """Write a temperature record."""
        # writing to csv file
        if not exists(self.filename):
            self.create()

        with open(self.filename, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({"Timestamp": timestamp,
                             "Centigrade": round(centigrade, 1),
                             "Fahrenheit": round(fahrenheit, 1),
                             "Humidity": round(humidity, 1)})

    def create(self):
        """Create a temperature csv file with a header row,"""
        # writing to csv file
        with open(self.filename, 'w', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            writer.writeheader()

    def read_last_line(self, n=1):
        """Returns the nth before last line of a file (n=1 gives last line)"""
        if self.exists:
            num_newlines = 0
            with open(self.filename, 'rb') as f:
                try:
                    f.seek(-2, os.SEEK_END)
                    while num_newlines < n:
                        f.seek(-2, os.SEEK_CUR)
                        if f.read(1) == b'\n':
                            num_newlines += 1
                except OSError:
                    f.seek(0)
                self.data = f.readline().decode()

    def refresh_data(self, initialise=False, debug=False):
        if self.exists:
            age_seconds = (datetime.now() - self.refresh_time).total_seconds()
            # If older than 10 minutes and there is data.
            if age_seconds > self.refresh_seconds or initialise:
                self.read_last_line()
                self.temp_c = f'{round(float(self.data.split(",")[1]))}`C'
                self.temp_f = f'{round(float(self.data.split(",")[2]))}`F'
                self.humidity = f'{round(float(self.data.split(",")[3]))}%'
                self.refresh_time = datetime.now()

    def get_temp_c(self, debug=False):
        """Returns the last recorded temperature Centigrade """
        self.refresh_data(debug=debug)
        return self.temp_c

    def get_temp_f(self):
        """Returns the last recorded temperature Fahrenheit """
        self.refresh_data()
        return self.temp_f

    def get_humidity(self):
        """Returns the last recorded humidity """
        self.refresh_data()
        return self.humidity
