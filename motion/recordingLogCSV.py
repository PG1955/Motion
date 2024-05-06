import json
import os
import random
import time
# from datetime import datetime, time
from os.path import exists
from datetime import datetime, timedelta
import csv
from pathlib import Path

"""
Logs recording times.

Version Date        Description
v1.1    01/04/2024  Initial version.
v1.2    22/04/2024  Get recording status.

__author__ = "Peter Goodgame"
# __name__ = "RecordingLogCSV"
__version__ = "v1.2"
"""


class RecordingLogCSV:
    """Store Recording times."""

    def __init__(self):
        self.columns = ["Timestamp", "Duration"]
        self.filename = "recording.csv"
        self.lockfile = "recording.lock"
        self.clear_lock()
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.started = False
        self.duration = None
        self.data = None
        self.exists = os.path.exists(self.filename)

    def start_recording(self):
        """Start a recording session."""
        self.start_time = datetime.now().replace(microsecond=0)
        self.set_lock()
        print(f'Recording start time logged at {self.start_time}')

    def end_recording(self):
        """End a recording session and write a CSV record."""
        duration = None
        print(f'self.started: {self.started}')
        if self.start_time:
            self.end_time = datetime.now().replace(microsecond=0)
            duration = self.end_time - self.start_time
            self.write(self.end_time, duration)
            self.clear_lock()
            print(f'Recording end time logged at {self.end_time}')
        self.start_time = None
        self.end_time = None

    def set_lock(self):
        """Creates a lock file to indicate recording is in progress."""
        print('Create lock file.')
        # Create a file.txt at the specified path
        Path(self.lockfile).touch()

    def clear_lock(self):
        """Deletes the lock file to indicate recording is in progress."""
        try:
            os.remove(self.lockfile)
            print('Deleted lock file.')
        except FileNotFoundError:
            pass

    def get_last_record(self):
        try:
            with open(self.filename, 'r') as file:
                last_line = file.readlines()[-1]
            return last_line
        except FileNotFoundError:
            return "2024-04-01 12:00:00,0:00:01"

    # def get_elapsed_time(self):
    #     pass

    def get_status(self):
        """Get current status of the Motion system"""
        # Check lock.
        recording = os.path.exists(self.lockfile)
        # Load last entry in the filename.
        (et, d) = self.get_last_record().split(",")
        self.end_time = datetime.strptime(et, '%Y-%m-%d %H:%M:%S')
        (h, m, s) = d.split(":")
        # self.duration = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        # Calculate end time and elapsed_time since recording ceased.
        self.elapsed_time = datetime.now().replace(microsecond=0) - self.end_time
        data = {"Recording": recording, "Seconds": self.elapsed_time.total_seconds(),
                "Status changed time": self.end_time.strftime("%H:%M:%S")}
        return data

    def write(self, start_time, duration):
        """Write a temperature record."""
        if not exists(self.filename):
            self.create()

        with open(self.filename, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            timestamp = start_time.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({"Timestamp": timestamp,
                             "Duration": duration})

    def create(self):
        """Create a temperature csv file with a header row,"""
        # writing to csv file
        with open(self.filename, 'w', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            writer.writeheader()

    def get_duration(self, start_date=datetime.now() - timedelta(hours=12)):
        """Return the duration since start date which defaults to 12 hours ago."""
        total_duration = timedelta()
        with open(self.filename, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            # Iterate over each row in the CSV file
            for row in csv_reader:
                try:
                    dt = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    if dt > start_date:
                        (h, m, s) = row[2].split(":")
                        duration = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                        total_duration += duration
                except ValueError:
                    continue
        return total_duration


def test_load():
    rlc = RecordingLogCSV()
    try:
        while True:
            # Record for 10 to 100 seconds.
            record_time = random.randint(10, 100)
            # Idle time between recording is between 1 Minute and 10 minutes.
            idle_time = random.randint(60, 60 * 10)
            print(f'Wait time {record_time} seconds.')
            rlc.start_recording()
            time.sleep(record_time)
            rlc.end_recording()
            print(f'Waiting for {idle_time} Seconds.')
            time.sleep(idle_time)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        an_hour_ago = start_date = datetime.now() - timedelta(hours=1)
        print(f'Total duration is {rlc.get_duration(an_hour_ago)}')

    finally:
        print('Program Exit')


def test_status():
    rlc = RecordingLogCSV()
    try:
        while True:
            # Record for 10 to 15 seconds.
            record_time = random.randint(10, 15)
            # Idle time between recording is between 1 Minute and 2 minutes.
            idle_time = random.randint(5, 10, )
            print(f'Wait time {record_time} seconds.')
            rlc.start_recording()
            status = rlc.get_status()
            recording = status['Recording']
            seconds = status['Seconds']
            last_record_time = status['Status changed time']
            print(f'Recording: {recording} Seconds: {seconds} Status changed time: {last_record_time}')
            time.sleep(seconds)
            rlc.end_recording()
            time.sleep(4)
            print(f'Get Status after recording: {rlc.get_status()}')
            print(f'Waiting for {idle_time} Seconds.')
            time.sleep(idle_time)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        an_hour_ago = start_date = datetime.now() - timedelta(hours=1)
        print(f'Total duration is {rlc.get_duration(an_hour_ago)}')

    finally:
        print('Program Exit')


def simulate_motion():
    """Record for between 5 and 10 seconds then wait between 1 and 10 minutes."""
    print('Starting a simulation of motion.')
    rlc = RecordingLogCSV()
    try:
        while True:
            # Record for 5 to 15 seconds.
            record_time = random.randint(5, 10)
            idle_time = random.randint(5, 10)
            print(f'Wait time {record_time} seconds.')
            rlc.start_recording()
            status = rlc.get_status()
            recording = status['Recording']
            seconds = int(status['Seconds'])
            if seconds > (60 * 2):
                seconds = 60 * 2
            last_record_time = status['Status changed time']
            print(f'Recording: {recording} Seconds: {seconds} Status changed time: {last_record_time}')
            print(f'Sleeping for {seconds} seconds. ')
            time.sleep(seconds)
            rlc.end_recording()
            print(f'Get Status after recording: {rlc.get_status()}')
            print(f'Sleeping for {idle_time} seconds. ')
            time.sleep(idle_time)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        an_hour_ago = start_date = datetime.now() - timedelta(hours=1)
        print(f'Total duration is {rlc.get_duration(an_hour_ago)}')

    finally:
        print('Program Exit')


def main():
    # test_load()
    # test_status()
    simulate_motion()


if __name__ == "__main__":
    main()
