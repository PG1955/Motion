import os
import time
from datetime import datetime, timedelta
import csv

"""
VisitsCSV class.

Writes a CSV file containing the timestamp of each movement for analysis.
"""


class VisitsCSV:
    def __init__(self, debug=False):
        self.debug = debug
        self.filename = None
        self.object = None
        self.now = datetime.now()
        self.csv_file = "visits.csv"
        self.columns = ['Timestamp', 'Trigger Point', 'Trigger Point Base',
                        'Subtraction History', 'Subtraction Threshold']
        if not os.path.isfile(self.csv_file):
            self.create()

    def create(self):
        if self.debug:
            print('CSV:create')
        with open(self.csv_file, 'w', newline='') as file:
            # creating a csv dict writer object
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            _writer.writeheader()

    """
    Write a record
    """

    def write(self, trigger_point=0, trigger_point_base=0,
              subtraction_history=0, subtraction_threshold=0):
        if self.debug:
            print('CSV:write')
        if not os.path.exists(self.csv_file):
            self.create()
        self.now = datetime.now()
        with open(self.csv_file, 'a', newline='') as file:
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            timestamp = self.now.strftime("%Y-%m-%d %H:%M:%S")
            return _writer.writerow({"Timestamp": timestamp,
                                     'Trigger Point': trigger_point,
                                     'Trigger Point Base': trigger_point_base,
                                     'Subtraction History': subtraction_history,
                                     'Subtraction Threshold': subtraction_threshold})

    def test(self, timestamp, trigger_point=0, trigger_point_base=0,
             subtraction_history=0, subtraction_threshold=0):
        if self.debug:
            print('CSV:write')
        if not os.path.isfile(self.csv_file):
            self.create()
        with open(self.csv_file, 'a', newline='') as file:
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return _writer.writerow({"Timestamp": timestamp,
                                     'Trigger Point': trigger_point,
                                     'Trigger Point Base': trigger_point_base,
                                     'Subtraction History': subtraction_history,
                                     'Subtraction Threshold': subtraction_threshold})

    def delete(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
            return True
        return False


def main():
    visit = VisitsCSV()
    # visit.delete()
    print("Running visitsCSV.main")
    now = datetime.now()
    recs = 10
    for cnt in range(recs):
        now += timedelta(minutes=30)
        visit.test(now, trigger_point=15, trigger_point_base=2, subtraction_history=100, subtraction_threshold=40)


# if __name__ == "__main__":
#     main()
