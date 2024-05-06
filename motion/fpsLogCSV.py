import os
import time
from os.path import exists
from datetime import datetime, timedelta
import csv
import psutil

__author__ = "Peter Goodgame"
__name__ = "fpsLogCSV"
__version__ = "v1.2"

from pathlib import Path


class FPSLogCSV:
    """Store Average Frames Per Second readings over time.
    set the number of seconds between recordings when using the monitor_fps."""

    def __init__(self, expected_fps, monitor_interval=60):
        self.fps = None
        self.expected_fps = expected_fps
        self.actual_fps = None
        self.sample_cnt = 0
        self.elapsed_time = None
        self.INTERVAL = monitor_interval
        self.data = None
        self.columns = ["Timestamp", "Expected Frames Per Second", "Actual Frames Per Second",
                        "Virtual Memory Size", "Resident Memory Size", "Shared Memory Size"]
        self.filename = "fps.csv"
        self.signal_filename = "fps.sig"
        self.refresh_time = datetime.now()
        self.now = datetime.now()
        self.refresh_seconds = 60 * 15
        self.exists = os.path.exists(self.filename)
        self.refresh_data(initialise=True)
        self.start_time = time.time()
        self.end_time = None

    def write(self, fps):
        """Write a FPS record."""
        # writing to csv file
        if not exists(self.filename):
            self.create()

        with open(self.filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.columns)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            if os.name == 'nt':
                vms = 1000
                rss = 1000
                shr = 1000
            else:
                vms = round(psutil.Process().memory_info().vms / 1024 / 1024, 2)
                rss = round(psutil.Process().memory_info().rss / 1024 / 1024, 2)
                shr = round(psutil.Process().memory_info().shared / 1024 / 1024, 2)

            writer.writerow({"Timestamp": timestamp,
                             "Expected Frames Per Second": self.expected_fps,
                             "Actual Frames Per Second": round(fps, 2),
                             "Virtual Memory Size": vms,
                             "Resident Memory Size": rss,
                             "Shared Memory Size": shr})
        Path(self.signal_filename).touch()

    def create(self):
        """Create a fps.csv file with a header row,"""
        # writing to csv file
        with open(self.filename, 'w', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            writer.writeheader()

    def delete(self):
        """Remove the file if it exists"""
        if os.path.exists(self.filename):
            os.remove(self.filename)
            print(f'Removed {self.filename} ')

    def refresh_data(self, initialise=False, debug=False):
        if self.exists:
            age_seconds = (datetime.now() - self.refresh_time).total_seconds()
            # If older than 10 minutes and there is data.
            if age_seconds > self.refresh_seconds or initialise:
                self.read_last_line()
                self.fps = f'{round(float(self.data.split(",")[1]),1)} FPS'
                self.refresh_time = datetime.now()

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

    def get_fps(self, debug=False):
        """Returns the last recorded frames per second"""
        self.refresh_data(debug=debug)
        return self.actual_fps

    def monitor_fps(self):
        self.sample_cnt += 1
        elapsed = round(time.time() - self.start_time)
        # print(f'Elapsed:{elapsed}')
        if elapsed >= self.INTERVAL:
            self.end_time = time.time()
            self.elapsed_time = round(self.end_time - self.start_time)
            self.actual_fps = round(self.sample_cnt / self.elapsed_time)
            self.write(self.actual_fps)
            self.start_time = self.end_time
            # print(f'Sample Cnt: {self.sample_cnt} / qElapsed time: {elapsed} ')
            self.sample_cnt = 0
        return self.actual_fps



