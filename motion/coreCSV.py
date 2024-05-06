import os
from os.path import exists
from datetime import datetime, timedelta
import csv


class CoreCSV:
    """Store Core information over time."""

    def __init__(self):
        self.arm_freq_min = None
        self.sdram_freq = None
        self.over_voltage_avs_boost = None
        self.throttled = None
        self.temp = None
        self.sdram_p_volt = None
        self.sdram_i_volt = None
        self.sdram_c_volt = None
        self.core_volt = None
        self.v3d_freq = None
        self.isp_freq = None
        self.h264_freq = None
        self.frequency48 = None
        self.over_voltage_avs = None
        self.gpu_freq_min = None
        self.gpu_freq = None
        self.core_freq_min = None
        self.core_freq = None
        self.arm_freq = None
        self.TXT_NAME = "coredata.txt"
        self.CSV_NAME = "coredata.csv"
        self.columns = ["Timestamp",
                        "arm_freq",
                        "arm_freq_min",
                        "core_freq",
                        "core_freq_min",
                        "gpu_freq",
                        "gpu_freq_min",
                        "over_voltage_avs",
                        "over_voltage_avs_boost",
                        "sdram_freq",
                        "arm: frequency(48)",
                        "core: frequency(1)",
                        "h264: frequency(28)",
                        "isp: frequency(45)",
                        "v3d: frequency(46)",
                        "core: volt",
                        "sdram_c: volt",
                        "sdram_i: volt",
                        "sdram_p: volt",
                        "temp",
                        "throttled"]

    def write(self):
        """Write a core data record."""
        if not exists(self.CSV_NAME):
            self.create()

        with open(self.CSV_NAME, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(({"Timestamp": timestamp,
                              "arm_freq": self.arm_freq,
                              "arm_freq_min": self.arm_freq_min,
                              "core_freq": self.core_freq,
                              "core_freq_min": self.core_freq_min,
                              "gpu_freq": self.gpu_freq,
                              "gpu_freq_min": self.gpu_freq_min,
                              "over_voltage_avs": self.over_voltage_avs,
                              "over_voltage_avs_boost": self.over_voltage_avs_boost,
                              "sdram_freq": self.sdram_freq,
                              "arm: frequency(48)": self.arm_freq,
                              "core: frequency(1)": self.core_freq,
                              "h264: frequency(28)": self.h264_freq,
                              "isp: frequency(45)": self.isp_freq,
                              "v3d: frequency(46)": self.v3d_freq,
                              "core: volt": self.core_volt,
                              "sdram_c: volt": self.sdram_c_volt,
                              "sdram_i: volt": self.sdram_i_volt,
                              "sdram_p: volt": self.sdram_p_volt,
                              "temp": self.temp,
                              "throttled": self.throttled}))

    def create(self):
        """Create a core csv file with a header row,"""
        # writing to csv file
        with open(self.CSV_NAME, 'w', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=self.columns)
            # writing headers (field names)
            writer.writeheader()

    def import_data(self):
        with open(self.TXT_NAME, 'r', newline='') as file:
            for line in file:

                data = line.replace('V', '').replace('\'C','') \
                    .replace('\n', '').replace('\t', '').split(sep='=')
                print(data)

                if data[0] == 'arm_freq':
                    self.arm_freq = data[1]
                elif data[0] == 'arm_freq_min':
                    self.arm_freq_min = data[1]
                elif data[0] == 'core_freq':
                    self.core_freq = data[1]
                elif data[0] == 'core_freq_min':
                    self.core_freq_min = data[1]
                elif data[0] == 'gpu_freq':
                    self.gpu_freq = data[1]
                elif data[0] == 'gpu_freq_min':
                    self.gpu_freq_min = data[1]
                elif data[0] == 'over_voltage_avs':
                    self.over_voltage_avs = data[1]
                elif data[0] == 'over_voltage_avs_boost':
                    self.over_voltage_avs_boost = data[1]
                elif data[0] == 'sdram_freq':
                    self.sdram_freq = data[1]
                elif data[0] == 'arm:frequency(48)':
                    self.arm_freq = data[1]
                elif data[0] == 'core:frequency(1)':
                    self.core_freq = data[1]
                elif data[0] == 'h264:frequency(28)':
                    self.h264_freq = data[1]
                elif data[0] == 'isp:frequency(45)':
                    self.isp_freq = data[1]
                elif data[0] == 'v3d:frequency(46)':
                    self.v3d_freq = data[1]
                elif data[0] == 'core:volt':
                    self.core_volt = data[1]
                elif data[0] == 'sdram_c:volt':
                    self.sdram_c_volt = data[1]
                elif data[0] == 'sdram_i:volt':
                    self.sdram_i_volt = data[1]
                elif data[0] == 'sdram_p:volt':
                    self.sdram_p_volt = data[1]
                elif data[0] == 'temp':
                    self.temp = data[1]
                elif data[0] == 'throttled':
                    self.throttled = data[1]

        # Write CSV line.
        self.write()


## Run Class.
c = CoreCSV()
c.import_data()
exit(0)
