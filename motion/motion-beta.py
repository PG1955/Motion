"""
Motion for Python3. Emulates MotionEye but uses tne libcamera library
Arducam low light camera.

Version Date        Description
v1.10   13/01/2022  Initial version of motion.
v1.11   04/02/2022  Add post_capture parameter and buffer_frame,
v1.13   14/02/2022  Added support for bgr colors in the ini file.
v1.14   18/02/2022  Added support for a dummy libcamera file to allow development on windows.
v1.15   19/02/2022  Only trigger recording after the average movement level exceeds sensitivity for .
v1.16   20/02/2022  Add report motion average peak.
v1.17   23/02/2022  Add recording_trigger logic. Tidy stats and include exposure.
v1.18   23/02/2022  Add a graph panel thanks to Rune.
v1.19   25/02/2022  Coloured graph with scaling,
v1.20   26/02.2022  Caluculate scalling factor. Rename sensitivity_level trigger_point.
v1.21   27/02/2022  Rotate image 180.
v1.22   01/03/2022  Add peak movement information to statistics.
v1.23   05/03/2022  Take jpg from at the point of peak movement.
v1.24   06/03/2022  Correct duplicate box printing.
v1.25   06/03/2022  Allow control of what is added to the jpg file. Graph and statistics.
v1.26   08/03/2022  Enlarge date and add seconds.
v1.27   09/03/2022  Allow various resolutions.
v1.28   10/03/2022  Position graph based on screen resolution.
v1.29.  11/03/2022  flip image.
v1.30   12/03/2022  Use on and off to specify boolean switches in the ini file.
v1.31   14/03/2022  Increase sensitivity and add parameter accumulateWeightedAlpha.
v1.32   18/03/2022  Performance enhancement and position date.
v1.33   09/04/2033  Add timelapse output.
v1.34   10/04/2022  Add display_frame_cnt option for test purposes.
v1.35.  01/05/2022 Correct box logic.
v1.36   19/06/2022 Only rotate the frame when writing to lessen the CPU load and reduce the core temperature.
v1.37   03/07/2022 Add output of a csv file showing peak movement values.
v1.38   12/07/2022 Log movement.
v1.39   14/07/2022 Write a csv movement record when mov
v1.40   17/07/2022 Add timings.
v2.00   20/07/2022 Eliminate the need to libcamera.
v2,01   20/07/2022 Use alternative motion detection.
v2.02   27/07/2022 Add subtraction_history parameter.
v2.03   03/08/2022 Mark the start and end of recording on the graph.
                    Also print date at the top if graph is active.
v2.04   04/08/2022 Adjust and make a pretty record and end icons on the graph.
v2.05   08/08/2022 Convert to run on picamera2.
v2.06   10/08/2022 Display te ROI square on jpg or mp4.
v2.07   01/09/2022 Add a mask file for creating a ROI.
v2.08   08/09/2022 Add parameter to specify box thickness and font size.
v3.00   11/09/2022 Convert fully to picamera2.
v3.00   11/09/2022 Add YOLO option.
v3.01   13/09/2022 Replace MotionCSV class with an external one.
v3.02   14/09/2022 Enable writing of a jpg showing te the highest movement for YOLO analysis.
v3.03   13/10/2022 If a file called tuning.json is found load it.
v3.04   15/10/2022 Enable SIGURS2 signal to re-output timings.
v3.05   20/10/2022 Add camera_tuning_file parameter. Only effective with rpi.
v3.06   22/10/2022 Add function to zoom in the image via zoom_factor.
v3.07   26/10/2022 Fix bug where maks file does not exist.
v3.08   26/10/2022 Save a clean version of the jpg to the timelapse dir.
v3.09   12/11/2022 Performance enhancements.
v3.10b  09/02/2023 Tinker with controls.
v3.11b  11/01/2023 Correct video buffer logic.
v3.11   13/02/2023 release motion.py
v3.12   20/-2/2023 Correct frame of highest movement on statistics.
v3.13   23/02/2023 Correct frames required count.
v3.14   03/03/2023 Correct Graph logic.
v3.15   07/03/2023 Revisit Graph.
v3.16   09/03/2023 Include camera controls.
v3.17   09/04/2023 Include visits csv.
v3.18   27/04/2023 Include settings in the visits.csv file.
v3.19   17/12/2023 Add Version class and MovementCSV class.
v3.20   17/11/2023 Major amendment to use of movement buffers to use advance motion triggering.
v3.21   31/12/2023 Tidy code and implement beta version for testing mean motion detection.
v3.22   03/01/2024 Amend triggerCSV layout to include extra trigger point data.
"""
__author__ = "Peter Goodgame"
__name__ = "motion"
__version__ = "v3.22b"

import argparse
import collections
import configparser
import csv
import logging
import math
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from Journal import journal
from MotionMP4 import MotionMP4
import pandas as pd
from picamera2 import Picamera2
from libcamera import controls
from visitsCSV import VisitsCSV
from triggerCSV import TriggerCSV


class TriggerMotion:
    sig_usr1 = False

    def __init__(self):
        if not os.name == 'nt':
            signal.signal(signal.SIGUSR1, self.trigger_motion)

    def trigger_motion(self, *args):
        self.sig_usr1 = True


class TriggerOutput:
    sig_usr2 = False

    def __init__(self):
        if not os.name == 'nt':
            signal.signal(signal.SIGUSR2, self.trigger_output)

    def trigger_output(self, *args):
        self.sig_usr2 = True


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


class MovmentTracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0

    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 25:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        return objects_bbs_ids


class Graph:
    """
    Draws a graph plotting movement levels.
    """

    def __init__(self, g_width, g_height, boarder, g_trigger_point_base, g_trigger_point):
        self.b = boarder
        self.yp = 10
        self.y = int((self.yp * g_height) / 100)
        self.x = int(g_width - self.b - self.b)
        self.g_trigger_point = g_trigger_point
        self.g_trigger_point_base = g_trigger_point_base
        self.scaling_factor = 4
        self.scaling_value = (self.y / self.scaling_factor) / self.g_trigger_point
        self.graph = np.zeros((self.y, self.x, 3), np.uint8)
        self.icon_buffer_list = []
        self.icon_size = round(self.y * 0.5)
        # print(f'Graph shape is: {self.graph.shape}')

    def update_frame(self, value):
        scaled_value = int(value * self.scaling_value)
        scaled_tp = int(self.g_trigger_point * self.scaling_value)
        scaled_btp = int(self.g_trigger_point_base * self.scaling_value)
        if scaled_value < 0:
            scaled_value = 0
        elif scaled_value >= self.y:
            scaled_value = self.y - 1
        new_graph = np.zeros((self.y, self.x, 3), np.uint8)
        new_graph[:, :-1, :] = self.graph[:, 1:, :]
        green = 0, 255, 0
        yellow = 0, 227, 255
        amber = 0, 183, 245
        white = 255, 255, 255

        if scaled_value > scaled_tp:
            new_graph[self.y - scaled_btp:, -1, :] = white
            new_graph[self.y - scaled_tp:self.y - scaled_btp, -1, :] = amber
            new_graph[self.y - scaled_value:self.y - scaled_tp, -1, :] = green
        else:
            if scaled_value > scaled_btp:
                new_graph[self.y - scaled_btp:, -1, :] = white
                new_graph[self.y - scaled_value:self.y - scaled_btp, -1, :] = amber
            else:
                if scaled_value > 0:
                    new_graph[(self.y - scaled_value):, -1, :] = white

        if len(self.icon_buffer_list) > 0:
            top, bottom, color = self.icon_buffer_list.pop(0)
            new_graph[top: bottom, -1, :] = color
        self.graph = new_graph

    def put_start_icon(self):
        red = 0, 0, 255
        black = 255, 255, 255
        self.graph = np.zeros((self.y, self.x, 3), np.uint8)
        for i in reversed(range(self.icon_size)):
            top = int((self.y / 2) - (i / 2))
            bottom = int((self.y / 2) + (i / 2))
            self.icon_buffer_list.append([top, bottom, red])
        return True

    def put_pause_icon(self):
        red = 0, 0, 255
        black = 0, 0, 0
        color = black
        for i in range(self.icon_size):
            if i < 2:
                color = red
            elif i < 4:
                color = black
            elif i < 6:
                color = red
            top = int((self.y / 2) - self.icon_size / 2)
            bottom = int((self.y / 2) + self.icon_size / 2)
            self.icon_buffer_list.append([top, bottom, color])
        return False

    def put_stop_icon(self):
        """Draws a stop icon on the graph."""
        red = 0, 0, 255
        color = red
        top = int((self.y / 2) - (self.icon_size / 2))
        bottom = int((self.y / 2) + (self.icon_size / 2))
        for i in range(self.icon_size):
            self.icon_buffer_list.append([top, bottom, color])
        return False

    def get_icon_size(self):
        return self.icon_size

    def get_graph(self):
        return self.graph

    def get_roi(self, g_frame):
        return g_frame[-abs(self.y + self.b):-abs(self.b), -abs(self.x + self.b):-abs(self.b), :]


class timingsCSV:
    """
    This class will output timing data4.
    maximum is the maximum number of records written default is 100.
    """

    def __init__(self, enabled=False, grace=1):
        self.enabled = enabled
        self.grace = grace
        self.record_cnt = 0
        self.point = None
        self.index = 0
        self.started = False
        self.dict = {}
        self.milliseconds = None
        self.last_ms = 0
        self.current_ms = 0
        self.time_ms = 0
        self.csv_file = "timings.csv"
        self.columns = header = ['Point', 'Milliseconds']
        self.delete()
        self.create()

    def lookup_point(self, point):
        result = self.dict.get(point)
        if not result:
            self.index += 1
            self.dict[point] = self.index
        n = str(self.dict[point]).zfill(2)
        return f'{n}-{point}'

    def log_point(self, point, start=False):
        if self.enabled and (self.started or start):
            self.started = True
            self.point = self.lookup_point(point)
            self.current_ms = round(time.time() * 2000)
            if self.last_ms > 0:
                self.milliseconds = self.current_ms - self.last_ms
                self.write()
            self.last_ms = self.current_ms

    def delete(self):
        if self.enabled:
            if os.path.exists(self.csv_file):
                os.remove(self.csv_file)

    def create(self):
        if self.enabled:
            self.record_cnt = 0
            with open(self.csv_file, 'w', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                _writer.writeheader()

    def write(self):
        if self.enabled:
            self.record_cnt += 1
            if self.record_cnt > self.grace:
                with open(self.csv_file, 'a', newline='') as file:
                    _writer = csv.DictWriter(file, fieldnames=self.columns)
                    _writer.writerow({"Point": self.point,
                                      "Milliseconds": self.milliseconds})
                # Limit size to 1000 records.
                if self.record_cnt > 1000 + self.grace:
                    self.enabled = False
                    Path('timings.sig').touch()
                return True
            else:
                return False


class fpsCSV:
    """
    Create a csv file showing how many frames are processed each second.
    """

    def __init__(self, target_fps):
        self.maximum = 200  # Maximum number of records to write.
        self.record_cnt = 0  # Number of records written.
        self.frame_cnt = 0  # Frames processed.
        self.csv_file = "frames-per-second.csv"
        self.columns = header = ['Seconds', 'Target', 'FPS']
        self.delete()
        self.create()
        self.now = 0
        self.start = 0
        self.target_fps = target_fps

    def delete(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        self.record_cnt = 0

    def create(self):
        self.record_cnt = 0
        with open(self.csv_file, 'w', newline='') as file:
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            _writer.writeheader()

    def write(self):
        if self.record_cnt < self.maximum:
            self.record_cnt += 1
            with open(self.csv_file, 'a', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                _writer.writerow({"Seconds": self.record_cnt,
                                  'Target': self.target_fps,
                                  'FPS': self.frame_cnt})
            self.frame_cnt = 0
            return True
        else:
            return False

    def cycle(self):
        self.frame_cnt += 1
        now = time.perf_counter()
        if self.start == 0:
            self.start = now
        duration = round(now - self.start, 2)
        if duration > 1:
            self.start = now
            return self.write()


class Yolo:
    def __init__(self):
        self.weights = 'Motion/props/yolov3.weights'
        self.cfg = 'Motion/props/yolov3.cfg'
        self.coco_names = 'Motion/props/coco.names'
        self.net = cv2.dnn.readNet(self.weights, self.cfg)
        classes = []
        with open(self.coco_names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        self.colors = np.random.uniform(0, 255, size=(len(classes), 3))
        self.blob = None
        self.image = None
        self.outs = None
        self.width = None
        self.height = None

    def detect_objects(self, image):
        self.image = image
        self.height, self.width, self.channels = image.shape
        # Detecting objects
        self.blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(self.blob)
        self.outs = self.net.forward(self.output_layers)

    def display_obects(self):
        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in self.outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * self.width)
                    center_y = int(detection[1] * self.height)
                    w = int(detection[2] * self.width)
                    h = int(detection[3] * self.height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        return self.image


class FPS:
    def __init__(self, avarageof=50):
        self.frametimestamps = collections.deque(maxlen=avarageof)

    def __call__(self):
        self.frametimestamps.append(time.time())
        if (len(self.frametimestamps) > 1):
            return len(self.frametimestamps) / (self.frametimestamps[-1] - self.frametimestamps[0])
        else:
            return 0.0

    def get_fps(self):
        if (len(self.frametimestamps) > 1):
            return len(self.frametimestamps) / (self.frametimestamps[-1] - self.frametimestamps[0])
        else:
            return 0.0


class Version:
    def __init__(self):
        """
        This class handles the output version numbering.
        """
        self.vparse = configparser.ConfigParser()
        self.vparse.read('version.ini')
        self.version = int(self.vparse.get('MP4', 'version'))

    def get_version(self):
        """
        Gets the current version number.
        """
        self.version += 1
        return self.version

    def write_version(self):
        """
        Updates the version number and returns the next number.
        """
        # Update ini file.
        self.vparse = configparser.ConfigParser()
        self.vparse.read('version.ini')
        self.vparse.set('MP4', 'version', str(self.get_version()))
        fp = open('version.ini', 'w')
        self.vparse.write(fp)
        fp.close()
        return self.version


class MovementCSV:
    def __init__(self, debug=False, interval=60):
        self.debug = debug
        self.interval = interval
        self.trigger_point = 0
        self.trigger_point_frames = 0
        self.subtraction_threshold = 0
        self.subtraction_history = 0
        self.motion_level = 0  # Current motion level.
        self.motion_highest = 0  # Maximum movement in the reporting period.
        self.movement_level = 0  # Current Movement level.
        self.movement_highest = 0  # Maximum movement in the reporting period.
        self.movement_average = 0  # Average movement based on mean movement.
        self.movement_total = 0  # Total movement
        self.movement_cnt = 0  # Number of frames.
        self.trigger_highest = 0  # value that triggered movement.
        self.trigger_point_base = 0  # value at which recording stops.
        self.tp_buffer_size = 30  # the number of records stored in the buffer.
        self.tp_buffer = np.zeros((self.tp_buffer_size, 4), np.dtype('uint8'))  # Used to store the past n movements.
        self.tp_buffer_ptr = 0
        self.movement_history_window = 0  # Number of past frames to Calculate the average movement level.
        self.movement_history_age = 0  # Number of frames gap between the movement history frames and the current one.
        self.variable_trigger_point = 0  # Variable trigger point = movement_average + trigger point
        self.last_write_time = datetime.now()  # Last write time.
        self.now = datetime.now()
        self.csv_file = "peakMovement.csv"
        self.columns = ['Timestamp',
                        'Trigger Point',
                        'Trigger Point Base',
                        'Movement History Window',
                        'Movement History Age',
                        'Subtraction Threshold',
                        'Subtraction History',
                        'Average',
                        'Variable Trigger Point',
                        'Variable Trigger Point Base',
                        'Highest Peak',
                        'Trigger Value']

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
    Called after the parameters are read.
    """

    def update_parameters(self, _trigger_point,
                          _trigger_point_base,
                          _trigger_point_frames,
                          _subtraction_threshold,
                          _subtraction_history,
                          _movement_history_window,
                          _movement_history_age):
        if self.debug:
            print('CSV:update_parameters')
        self.trigger_point = _trigger_point
        self.trigger_point_base = _trigger_point_base
        self.trigger_point_frames = _trigger_point_frames
        self.subtraction_threshold = _subtraction_threshold
        self.subtraction_history = _subtraction_history
        self.movement_history_window = _movement_history_window
        self.movement_history_age = _movement_history_age
        if not os.path.isfile(self.csv_file):
            self.create()

    def log_level(self,
                  ll_movement_level,
                  ll_movement_level_average,
                  ll_variable_trigger_point,
                  ll_variable_trigger_point_base):
        """
        Call this for every frame read that is read.
        """
        if self.debug:
            print('CSV:log_level')
        if not os.path.isfile(self.csv_file):
            self.create()
        if ll_movement_level > 0:
            self.movement_cnt += 1
            self.movement_total += ll_movement_level
        if ll_movement_level > self.movement_highest:
            self.movement_highest = ll_movement_level
        self.now = datetime.now()
        diff = self.now - self.last_write_time
        minutes = round((diff.total_seconds()), 2)
        # minutes = round((diff.total_seconds() / 60), 2)
        if minutes >= self.interval:
            if self.debug:
                print(f'round({self.movement_total} / {self.movement_cnt})')
            if self.movement_cnt > 0:
                self.movement_average = round(self.movement_total / self.movement_cnt)
            else:
                self.movement_average = 0
            self.write()
            self.last_write_time = self.now
            self.movement_total = 0
            self.movement_cnt = 0
            self.movement_highest = 0

    def log_motion(self, _motion_level):
        """
        To be called when motion is detected.
        if sighup is set to true a record is written with
        values set temporarily set to 1.
        """
        if self.debug:
            print('CSV:log_motion')
        if not os.path.isfile(self.csv_file):
            self.create()
        if self.trigger_highest < _motion_level:
            self.trigger_highest = _motion_level

    def motion_write(self, sighup=False):
        """
        Call this after motion comes to an end.
        """
        if self.debug:
            print('CSV:motion_write')
        if not os.path.isfile(self.csv_file):
            self.create()
        if not sighup:
            with open(self.csv_file, 'a', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                timestamp = self.now.strftime("%Y-%m-%d %H:%M")
                _writer.writerow({"Timestamp": timestamp,
                                  'Trigger Point': self.trigger_point,
                                  'Trigger Point Base': self.trigger_point_base,
                                  'Movement History Window': self.movement_history_window,
                                  'Movement History Age': self.movement_history_age,
                                  'Subtraction Threshold': self.subtraction_threshold,
                                  'Subtraction History': self.subtraction_history,
                                  "Average": self.movement_average,
                                  "Highest Peak": self.movement_highest,
                                  "Trigger Value": self.trigger_highest,
                                  "Variable Trigger Point": self.movement_average + self.trigger_point,
                                  "Variable Trigger Point Base": self.movement_average + self.trigger_point_base})
            self.trigger_highest = 0
        else:
            with open(self.csv_file, 'a', newline='') as file:
                _writer = csv.DictWriter(file, fieldnames=self.columns)
                timestamp = self.now.strftime("%Y-%m-%d %H:%M")
                _writer.writerow({"Timestamp": timestamp,
                                  'Trigger Point': 1,
                                  'Trigger Point Base': 1,
                                  'Movement History Window': self.movement_history_window,
                                  'Movement History Age': self.movement_history_age,
                                  'Subtraction Threshold': self.subtraction_threshold,
                                  'Subtraction History': self.subtraction_history,
                                  "Average": 1,
                                  "Highest Peak": 1,
                                  "Trigger Value": 1})

    def write(self):
        """
        Called every minute.
        """
        if self.debug:
            print('CSV:write')
        if not os.path.isfile(self.csv_file):
            self.create()
        with open(self.csv_file, 'a', newline='') as file:
            _writer = csv.DictWriter(file, fieldnames=self.columns)
            timestamp = self.now.strftime("%Y-%m-%d %H:%M")
            return _writer.writerow({"Timestamp": timestamp,
                                     'Trigger Point': self.trigger_point,
                                     'Trigger Point Base': self.trigger_point_base,
                                     'Movement History Window': self.movement_history_window,
                                     'Movement History Age': self.movement_history_age,
                                     'Subtraction Threshold': self.subtraction_threshold,
                                     'Subtraction History': self.subtraction_history,
                                     "Average": self.movement_average,
                                     "Highest Peak": self.movement_highest,
                                     "Trigger Value": 0,
                                     "Variable Trigger Point": self.movement_average + self.trigger_point,
                                     "Variable Trigger Point Base": self.movement_average + self.trigger_point_base})


class MP4:

    def __init__(self, path, mp4_size, mp4_frame_rate):
        self.path = path
        self.size = mp4_size
        self.frame_rate = mp4_frame_rate
        self.version = 0
        self.writer = None
        self.filename = None
        self.filepath = None
        self.avc1 = None
        self.mp4v = None

        if not os.path.exists(self.path):
            print('Creating output directory {}'.format(self.path))
            os.makedirs(self.path)

    def new_filename(self, nf_version):
        self.version = nf_version
        self.filename = str(self.version).zfill(3) + '-' + str(
            datetime.now().strftime('%Y%m%d%H%M%S')) + '.mp4'
        self.filepath = os.path.join(self.path + os.sep + self.filename)
        return self.filepath

    def open(self):
        # x264 = cv2.VideoWriter_fourcc(*'X264')
        self.avc1 = cv2.VideoWriter_fourcc(*'AVC1')
        self.mp4v = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(self.new_filename(self.version), self.mp4v, self.frame_rate, self.size)
        return self.writer

    def close(self):
        self.writer.release()
        self.writer = None

    def is_open(self):
        if self.writer:
            return True
        else:
            return False

    def get_filename(self):
        return self.filename

    def get_pathname(self):
        return self.filepath


# End Classes


# =============================================
# --- Global storage. -------------------------
# =============================================
global trigger_point
global trigger_point_base


def read_configuration(signalNumber, frame):
    print('(SIGHUP) reading configuration')
    return


def put_frame_cnt(pfc_frame, frame_count):
    # Write frame count.
    wt_font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(str(frame_count), wt_font, date_font_scale, date_font_thickness)
    boarder = 5
    line_height = text_size[1]
    line_length = text_size[0]
    wt_pos = 1 + boarder, line_height + boarder

    cv2.putText(pfc_frame,
                str(frame_count),
                wt_pos,
                wt_font,
                date_font_scale,
                date_rgb,
                date_font_thickness,
                cv2.LINE_AA)
    return pfc_frame


def flip_image(frame, hflip=False, vflip=False):
    if hflip and not vflip:
        frame = cv2.flip(frame, 0)
    elif vflip and not hflip:
        frame = cv2.flip(frame, 1)
    elif vflip and hflip:
        frame = cv2.flip(frame, -1)
    return frame


def put_date(wt_frame):
    # Write data4 and time on the video.
    wt_now = datetime.now()
    wt_text = wt_now.strftime("%Y-%m-%d %H:%M:%S")
    wt_font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(wt_text, wt_font, date_font_scale, date_font_thickness)
    boarder = 5
    line_height = text_size[1]
    line_length = text_size[0]
    if date_position == 'top' or draw_graph or draw_jpg_graph:
        wt_pos = lores_width - line_length - boarder, line_height + boarder
    else:
        wt_pos = lores_width - line_length - boarder, lores_height - line_height - boarder

    cv2.putText(wt_frame,
                wt_text,
                wt_pos,
                wt_font,
                date_font_scale,
                date_rgb,
                date_font_thickness,
                cv2.LINE_AA)
    return wt_frame


def put_text(pt_frame, pt_text, pt_color):
    position = (5, 20)  # indent and line
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA
    text_size, _ = cv2.getTextSize(pt_text, font, statistics_font_scale, statistics_font_thickness)
    line_height = text_size[1] + 5
    x, y0 = position
    for i, line in enumerate(pt_text.split("\n")):
        y = y0 + i * line_height
        cv2.putText(pt_frame,
                    line,
                    (x, y), font,
                    statistics_font_scale,
                    pt_color,
                    statistics_font_thickness,
                    line_type)
    return pt_frame


def add_statistics(ps_frame):
    exp_time = round(exposure_controls['ExposureTime'], 2)
    ana_gain = round(exposure_controls['AnalogueGain'], 2)
    ps_stats = f'Software version: {__version__}\n\
Frame rates: Record: {image_record_fps} Playback: {image_playback_fps}\n\
Exposure: {exp_time}, Gain: {ana_gain}\n\
Trigger Point: {trigger_point} Base  {trigger_point_base} \n\
Average Window {movement_window} Delay {movement_window_age} Frame Cnt {movement_frame_count}\n\
MOG2 Subtraction Threshold: {subtraction_threshold}\n\
MOG2 Subtraction History: {subtraction_history}\n\
Total Frames: {frames_written}\n\
Peak Movement: {movement_peak} at frame: {movement_peak_frame} \n\
FPS: {round(fps.get_fps(), 2)} \n\
Zoom Factor: {zoom_factor} \n\
Pre Movement Frames: {pre_frames} Post: {post_frames}'
    return put_text(ps_frame, ps_stats, statistics_rgb)


def write_jpg(wj_frame):
    jpg_path = mp4.get_pathname().replace('mp4', 'jpg')
    if statistics_jpg:
        wj_frame = add_statistics(wj_frame)
    if draw_jpg_graph:
        print(f'jpg shape is {np.shape(wj_frame)}')
        _roi = graph.get_roi(wj_frame)
        print(f'ROI: {np.shape(_roi)} get graph shape {np.shape(graph.get_graph())}')
        _roi[:] = graph.get_graph()

    # Draw roi on mp4 file.
    if display_roi_jpg and mask_path:
        wj_frame = draw_roi(mask_img, wj_frame, display_roi_rgb,
                            display_roi_thickness, display_roi_font_size)

    print('JPEG Path: {}'.format(jpg_path))
    cv2.imwrite(jpg_path, wj_frame)


def write_timelapse_jpg(wtl_frame):
    timelapse_path = os.path.join(os.getcwd(), "Motion/timelapse")
    if not os.path.isdir(timelapse_path):
        os.mkdir(timelapse_path)
    timelapse_jpg = os.path.join(timelapse_path, mp4.get_filename().replace('mp4', 'jpg'))
    print('JPEG Path: {}'.format(timelapse_jpg))
    cv2.imwrite(timelapse_jpg, wtl_frame)


def write_yolo_jpg(wyl_frame):
    yolo_path = os.path.join(os.getcwd(), "Motion/yolo")
    if not os.path.isdir(yolo_path):
        os.mkdir(yolo_path)
    yolo_jpg = os.path.join(yolo_path, mp4.get_filename().replace('mp4', 'jpg'))
    print('JPEG Path: {}'.format(yolo_jpg))
    cv2.imwrite(yolo_jpg, wyl_frame)


def run_cmd(rc_cmd):
    subprocess.call(rc_cmd, shell=True, executable='/bin/bash')


def get_logger():
    logger = logging.getLogger(__name__)
    # journald_handler = JournaldLogHandler()
    # journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    # logger.addHandler(journald_handler)
    logger.setLevel(logging.INFO)
    return logger


def add_box(ab_frame, ab_area, ab_label, ab_color, ab_thickness=1, ab_fontsize=1):
    x = ab_area[0]
    y = ab_area[1]
    w = ab_area[2]
    h = ab_area[3]
    cv2.rectangle(ab_frame, (x, y), (x + w, y + h), ab_color, 1)
    cv2.putText(ab_frame, ab_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, ab_fontsize, ab_color, ab_thickness)
    return ab_frame


def get_parameter(gp_parser, gp_name, gp_default):
    try:
        gp_ret = gp_parser.get('Motion', gp_name)
        print('{}: {}'.format(gp_name, gp_ret))
    except:
        gp_ret = gp_default
    if gp_ret == 'on':
        gp_ret = True
    elif gp_ret == 'off':
        gp_ret = False
    return gp_ret


def get_bgr(gb_str):
    red, green, blue = [int(c) for c in gb_str.split(',')]
    return (blue, green, red)


def next_index(_index, _buffer_size):
    _index += 1
    if _index >= _buffer_size:
        _index = 0
    return _index


def get_centre(contours):
    for i in contours:
        M = cv2.moments(i)
        if M['m00'] != 0:
            # cx = int(M['m10'] / M['m00'])
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
    return cx, cy


def draw_roi(mask, image, rgb, thickness, size):
    mask_edges = cv2.Canny(mask, 10, 100)
    contours, hierarchy = cv2.findContours(mask_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cx, cy = get_centre(contours)
    cv2.putText(image, 'ROI', (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, size, rgb, thickness, cv2.LINE_AA)
    cv2.drawContours(image, contours, -1, rgb, thickness)
    return image


def next_movement_index(nmi_index, nmi_buffer_size):
    nmi_index += 1
    if nmi_index >= nmi_buffer_size:
        nmi_index = 0
    return nmi_index


def Average(array):
    return round(sum(array) / len(array), 2)


"""
v3.20 Advanced movement detection """

"""
Return True if the number of frames containing movement exceeds the frame count ceiling.
"""


def check_frame_count():
    global consecutive_movement_frame_cnt
    print(f'{consecutive_movement_frame_cnt} >= {movement_frame_count}')
    if consecutive_movement_frame_cnt >= movement_frame_count:
        return True
    else:
        consecutive_movement_frame_cnt += 1
        return False


def zoom(img, zoom_factor=1.5):
    y_size = img.shape[0]
    x_size = img.shape[1]
    # define new boundaries
    x1 = int(0.5 * x_size * (1 - 1 / zoom_factor))
    x2 = int(x_size - 0.5 * x_size * (1 - 1 / zoom_factor))
    y1 = int(0.5 * y_size * (1 - 1 / zoom_factor))
    y2 = int(y_size - 0.5 * y_size * (1 - 1 / zoom_factor))
    # first crop image then scale
    img_cropped = img[y1:y2, x1:x2]
    return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_CUBIC)


def resize_img(rs_image, rs_size):
    rs_current_height = rs_image.shape[0]
    rs_current_width = rs_image.shape[1]
    rs_new_height = rs_size[0]
    rs_new_width = rs_size[1]
    if rs_current_width > rs_new_width or rs_current_height > rs_new_height:
        return cv2.resize(rs_image, rs_size, interpolation=cv2.INTER_AREA)
    elif rs_current_width < rs_new_width or rs_current_height < rs_new_height:
        return cv2.resize(rs_image, rs_size, interpolation=cv2.INTER_LINEAR)
    else:
        return rs_image


def get_exposure():
    # v3.10b report tuned exposure.
    _metadata = picam2.capture_metadata()
    _exposure_controls = {ec: _metadata[ec] for ec in ["ExposureTime", "AnalogueGain", "ColourGains"]}
    log.info(_exposure_controls)
    return _exposure_controls


def debug_size(_image):
    if debug:
        print(f'Image size is {_image.shape}')


"""
Start Program
"""
if __name__ == "motion":
    # mp.freeze_support()
    software_version = __version__

    # Check for arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Debug enabled')
    parser.add_argument('-s', '--signal', type=int, default=0, help='fire sigusr at frame number')

    args = parser.parse_args()
    # get an instance of the logger object this module will use
    log = get_logger()
    signal_frame = args.signal
    debug = args.debug

    if debug:
        log.debug('Debug os on')

    log.info('Software Version {}'.format(__version__))
    log.info('PID: {}'.format(os.getpid()))
    print('PID: {}'.format(os.getpid()))

    # Enable signals.
    killer = GracefulKiller()
    motion = TriggerMotion()
    output = TriggerOutput()

    # Read INI file.
    parser = configparser.ConfigParser()
    parser.read('motion.ini')

    box = get_parameter(parser, 'box', 'OFF')
    box_font_size = float(get_parameter(parser, 'box_font_size', '1'))
    box_jpg = get_parameter(parser, 'box_jpg', 'OFF')
    box_rgb = get_bgr(get_parameter(parser, 'box_rgb', '255,255,255'))
    box_thickness = int(get_parameter(parser, 'box_thickness', '1'))
    camera_controls = get_parameter(parser, 'camera_controls', 'off')
    camera_tuning_file = get_parameter(parser, 'camera_tuning_file', 'off')
    command = get_parameter(parser, 'command', 'None')
    csv_output = get_parameter(parser, 'csv_output', 'off')
    csv_timings = get_parameter(parser, 'csv_timings', 'off')
    csv_visits_log = get_parameter(parser, 'csv_visits_log', 'off')
    date_font_scale = float(get_parameter(parser, 'date_font_scale', '1.0'))
    date_font_thickness = int(get_parameter(parser, 'date_font_thickness', '1'))
    date_position = get_parameter(parser, 'date_position', 'none')
    date_rgb = get_bgr(get_parameter(parser, 'date_rgb', '255,255,255'))
    display = get_parameter(parser, 'display', 'off')
    display_frame_cnt = get_parameter(parser, 'display_frame_cnt', 'off')
    display_image_height = int(get_parameter(parser, 'display_image_height', '480'))
    display_image_width = int(get_parameter(parser, 'display_image_width', '640'))
    display_roi = get_parameter(parser, 'display_roi', 'off')
    display_roi_font_size = float(get_parameter(parser, 'display_roi_font_size', '0.5'))
    display_roi_jpg = get_parameter(parser, 'display_roi_jpg', 'off')
    display_roi_rgb = get_bgr(get_parameter(parser, 'display_roi_rgb', '255,255,255'))
    display_roi_thickness = int(get_parameter(parser, 'display_roi_thickness', '1'))
    draw_graph = get_parameter(parser, 'draw_graph', 'off')
    draw_jpg_graph = get_parameter(parser, 'draw_jpg_graph', 'off')
    grace_frames = int(get_parameter(parser, 'grace_frames', '0'))
    image_exposure = int(get_parameter(parser, 'exposure', '0'))
    image_height = int(get_parameter(parser, 'image_height', '480'))
    image_horizontal_flip = bool(get_parameter(parser, 'image_horizontal_flip', 'off'))
    image_playback_fps = int(get_parameter(parser, 'image_playback_fps', 30))
    image_record_fps = int(get_parameter(parser, 'image_record_fps', 30))
    image_vertical_flip = bool(get_parameter(parser, 'image_vertical_flip', 'off'))
    image_width = int(get_parameter(parser, 'image_width', '640'))
    lores_height = int(get_parameter(parser, 'lores_height', '360'))
    lores_width = int(get_parameter(parser, 'lores_width', '640'))
    main_height = int(get_parameter(parser, 'main_height', '720'))
    main_width = int(get_parameter(parser, 'main_width', '1280'))
    mask_path = get_parameter(parser, 'mask_path', 'off')
    movement_window = int(get_parameter(parser, 'movement_window', '0'))
    movement_window_age = int(get_parameter(parser, 'movement_window_age', '0'))
    movement_frame_count = int(get_parameter(parser, 'movement_frame_count', '0'))
    output_dir = get_parameter(parser, 'output_dir', 'Motion')
    post_frames = int(get_parameter(parser, 'post_frames', '1'))
    pre_frames = int(get_parameter(parser, 'pre_frames', '1'))
    stabilise = int(get_parameter(parser, 'stabilise', '10'))
    statistics = get_parameter(parser, 'statistics', 'off')
    statistics_font_scale = float(get_parameter(parser, 'statistics_font_scale', '1.0'))
    statistics_font_thickness = int(get_parameter(parser, 'statistics_font_thickness', '1'))
    statistics_jpg = get_parameter(parser, 'statistics_jpg', 'off')
    statistics_rgb = get_bgr(get_parameter(parser, 'statistics_rgb', '255,255,255'))
    subtraction_history = int(get_parameter(parser, 'subtraction_history', 100))
    subtraction_threshold = int(get_parameter(parser, 'subtraction_threshold', 40))
    timelapse_frame_number = int(get_parameter(parser, 'timelapse_frame_number', '0'))
    timings_cnt = int(get_parameter(parser, 'timings_cnt', '0'))
    trigger_point = int(get_parameter(parser, 'trigger_point', 200))
    trigger_point_base = int(get_parameter(parser, 'trigger_point_base', 100))
    trigger_point_csv_window = int(get_parameter(parser, 'trigger_point_csv_window', 0))
    trigger_point_frames = int(get_parameter(parser, 'trigger_point_frames', 1))
    yolo_detection = bool(get_parameter(parser, 'yolo_detection', 'off'))
    yolo_output = bool(get_parameter(parser, 'yolo_output', 'off'))
    zoom_factor = float(get_parameter(parser, 'zoom_factor', 0))

    # Instantiate movementCSV file writing.
    mcsv = None
    if csv_output:
        mcsv = MovementCSV()
        mcsv.update_parameters(trigger_point, trigger_point_base, trigger_point_frames, subtraction_threshold,
                               subtraction_history, movement_window, movement_window_age)

    # Instantiate Trigger CSV class,
    trigger_csv = TriggerCSV(trigger_point, trigger_point_base, trigger_point_csv_window, movement_window, movement_window_age)

    # Instantiate visits log.
    if csv_visits_log:
        visits = VisitsCSV()

    # Read the version ini file.
    version_class = Version()
    version_num = version_class.get_version()

    # Enable a graph.
    graph = Graph(lores_width, lores_height, 10, trigger_point_base, trigger_point)

    # Enable fps counting.
    fps = FPS()

    # Instantiate tracker.
    tracker = MovmentTracker()

    # Get mask image.
    if mask_path and os.path.exists(mask_path):
        mask_img = cv2.imread(mask_path)
        mask_height = mask_img.shape[0]
        mask_width = mask_img.shape[1]
        if not mask_width == lores_width:
            mask_img = resize_img(mask_img, (lores_width, lores_height))
            # mask_img = cv2.resize(mask_img, (lores_width, lores_height), interpolation=cv2.INTER_LINEAR)
        mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
        log.info(f'Loaded mask template {mask_path}')
    else:
        log.info('Mask template is not loaded')
        mask_path = False

    # Initialise Variables
    size = (lores_width, lores_height)
    average = None
    writer = None
    stabilisation_cnt = 0
    frames_required = 0  # Frames requested for this mp4 file
    frames_written = 0  # Frames written to this mp4 file.
    movement_peak = 0  # Monitor the highest level of movement.
    movement_peak_frame = 0  # Log the frame number where peak movement occurs.
    mean_average_movement = 0  # The average amount of movement than caused a trigger record.
    object_detector = cv2.createBackgroundSubtractorMOG2(history=subtraction_history,
                                                         varThreshold=subtraction_threshold)
    exposure_controls = None
    focus_controls = None
    consecutive_movement_frame_cnt = 0  # Used by motion detection.
    log.info('Initialise MP4 output')

    if camera_tuning_file and not os.name == 'nt':
        log.info(f'Using tuning file {camera_tuning_file}')
        tuning = Picamera2.load_tuning_file(camera_tuning_file)
        algo = Picamera2.find_tuning_algo(tuning, "rpi.agc")
        picam2 = Picamera2(tuning=tuning)
        picam2.set_controls({"FrameRate": int(image_record_fps)})
        log.info(f'Setting FPS to {image_record_fps}.')

        if camera_tuning_file == 'ov5647.json':
            picam2.set_controls({"AeExposureMode": controls.AeExposureModeEnum.Long})

        if camera_tuning_file == 'imx708.json':
            picam2.set_controls({"AfMode": controls.AfModeEnum.Auto,
                                 "AfMetering": controls.AfMeteringEnum.Auto})
            print('Set auto focus mode.')
            log.info('Set auto focus mode.')

        log.info(f'Using {camera_tuning_file} tuning file.')
    else:
        log.info('No tuning file specified in the motion.ini file.')
        picam2 = Picamera2()

    video_config = picam2.create_video_configuration(
        main={"size": (main_width, main_height), "format": "RGB888"})

    picam2.configure(video_config)
    picam2.set_controls({"FrameRate": image_record_fps})
    log.info(f'Frame rate set to {image_record_fps}.scp')

    picam2.start()
    time.sleep(2)

    # v3.10b report tuned exposure.
    exposure_controls = get_exposure()

    # Initialise video buffer_frame.
    index = 0
    buffer = np.zeros((pre_frames, lores_height, lores_width, 3), np.dtype('uint8'))
    buffered_frame = np.zeros((1, lores_height, lores_width, 3), np.dtype('uint8'))
    buffered_bounding_rect = np.zeros((pre_frames, 4), np.dtype('uint16'))
    buffered_movement = np.array([])
    jpg_frame = np.zeros((1, lores_height, lores_width, 3), np.dtype('uint8'))
    timelapse_frame = np.zeros((1, lores_height, lores_width, 3), np.dtype('uint8'))
    yolo_frame = np.zeros((1, main_height, main_width, 3), np.dtype('uint8'))
    yolo_peak_movement_frame = np.zeros((1, main_height, main_width, 3), np.dtype('uint8'))
    log.info('Camera started')

    # Instantiate mp4 output.
    mp4 = MP4(output_dir, size, image_playback_fps)

    if yolo_detection:
        yolo = Yolo()

    log.info('PID: {}'.format(os.getpid()))
    # Read images and process them.
    jpg_contour = 0
    movement_level = 0  # Movement level.
    movement_flag = False  # Set to true is movement is detected.
    movement_triggered = False  # Set only when processing the frame that triggered movement.
    movement_ended = False  # Set when movement ends.
    movement_frame_cnt = 0  # Number of frames since movement was detected.
    movement_total = 0  # Total contour count for consecutive frames.
    recording_flag = False  # True when the Graph indicates recording is in progress.
    frames_required = 0
    contour = (0, 0, 0, 0)
    resize = False
    stabilised = False
    signal_frame_cnt = 0
    average_window_cnt = 0  # Used to ensure all stored frame values are populated.

    # Instantiate timings.
    tcsv = timingsCSV(enabled=csv_timings, grace=subtraction_history)

    # =========================================
    # Main process loop.
    # =========================================
    while not killer.kill_now:
        # Read Images
        tcsv.log_point('Start Loop', start=True)
        main_frame = picam2.capture_array()
        tcsv.log_point('Read Frame')

        if not zoom_factor == 0:
            main_frame = zoom(main_frame, zoom_factor)
            tcsv.log_point(f'Zoom factor {zoom_factor}')

        # Resize the frame.
        frame = resize_img(main_frame, (lores_width, lores_height))
        tcsv.log_point('Resize Frame')

        # Rotate the image if needed.
        frame = flip_image(frame, image_horizontal_flip, image_vertical_flip)
        tcsv.log_point('Rotate Frame')

        # Log Frames per second.
        fps()

        # For debugging check frame number.
        if signal_frame > 0 and signal_frame_cnt < signal_frame:
            signal_frame_cnt += 1
            print(f'SigFrame: {signal_frame} Signal frame count: {signal_frame_cnt}')

        # Apply the mask.
        if mask_path:
            roi = cv2.bitwise_and(frame, frame, mask=mask_img)
            tcsv.log_point('Apply Mask')
        else:
            roi = frame

        # Detect movement.
        mask = object_detector.apply(roi)
        tcsv.log_point('Applied MOG2')
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        tcsv.log_point('Found contours')

        # Add timestamp.
        if date_position == 'top' or date_position == 'bottom':
            frame = put_date(frame)
            tcsv.log_point('Add Timestamp')

        # Save the frame to the buffer_frame.
        index = next_index(index, pre_frames)
        buffered_frame = np.copy(buffer[index])
        buffer[index] = frame

        # Stabilise the camera
        if not stabilised:
            jpg_frame = np.copy(buffer[index])
            yolo_peak_movement_frame = np.copy(main_frame)
            stabilisation_cnt += 1
            if stabilisation_cnt < stabilise + pre_frames:
                continue
            else:
                stabilised = True

        # find the biggest contour (c) by the area and save it.
        if len(contours) > 1:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            buffered_bounding_rect[index] = (x, y, w, h)
            # Append the values to the array then drop the obsolete values.
            movement_level = len(contours)
            buffered_movement = np.append(buffered_movement, movement_level)
        else:
            buffered_movement = np.append(buffered_movement, 0)
            buffered_bounding_rect[index] = (0, 0, 0, 0)

        # Trim the movement buffer.
        buffered_movement = buffered_movement[((movement_window + movement_window_age) + 1) * -1::]

        # Display the live feed.
        if display:
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            if key == 32:
                motion.sig_usr1 = True

            display_frame = resize_img(buffer[index], (display_image_width, display_image_height))
            cv2.imshow('Live Data', display_frame)

        # Get the average movement over the movement window using movement_window_age.
        mean_movement = round(np.mean(buffered_movement[:(movement_window + movement_window_age + 1)]))
        mean_trigger_point = mean_movement + trigger_point
        mean_trigger_point_base = mean_movement + trigger_point_base

        # Ensure the buffered_movement buffer is fully populated.
        if buffered_movement.size < movement_window + movement_window_age:
            continue

        old_mean_movement = round(
            np.mean(buffered_movement[-(movement_window + movement_window_age):-(movement_window_age - 1)]))
        old_mean_trigger_point_base = old_mean_movement + trigger_point_base
        old_mean_trigger_point = old_mean_movement + trigger_point

        # Check for movement. Compare the mean movement level with this movement level.
        # Do this after the movement buffer is complete.
        if movement_window_age > 0:
            trigger_csv.log_movement(old_mean_trigger_point, old_mean_trigger_point_base, mean_movement)
            if movement_flag:
                movement_triggered = False
                movement_ended = True
                if mean_movement < old_mean_trigger_point_base:
                    movement_flag = False
                    movement_ended = True
            else:
                # When movement_flag is not set.
                if mean_movement > old_mean_trigger_point:
                    movement_flag = True
                    movement_triggered = True
                    trigger_csv.movement_triggered()
        else:
            trigger_csv.log_movement(trigger_point, trigger_point_base, movement_level)
            if movement_flag:
                movement_triggered = False
                movement_ended = True
                if movement_level < trigger_point_base:
                    movement_flag = False
                    movement_ended = True
            else:
                if movement_level > trigger_point:
                    movement_flag = True
                    movement_triggered = True
                    trigger_csv.movement_triggered()

        tcsv.log_point('Check movement')

        # Send the motion level to the CSV class.
        if csv_output:
            mcsv.log_level(movement_level,
                           mean_movement,
                           mean_trigger_point,
                           mean_trigger_point_base)

        # Stabilise the camera
        if not stabilised:
            jpg_frame = np.copy(buffer[index])
            yolo_peak_movement_frame = np.copy(main_frame)
            stabilisation_cnt += 1
            if stabilisation_cnt < stabilise + pre_frames:
                continue
            else:
                stabilised = True

        # If SIGUSR1 trigger a mp4 manually.
        if motion.sig_usr1 or (signal_frame > 0 and signal_frame_cnt == signal_frame):
            log.info('Manual SIGUSR1 detected.')
            signal_frame = 0
            movement_flag = True
            movement_triggered = True
            movement_trigger_csv = True
            movement_trigger_csv_counter = movement_window_age
            jpg_frame = np.copy(buffer[index])
            yolo_peak_movement_frame = np.copy(main_frame)
            motion.sig_usr1 = False
            trigger_csv.movement_triggered()

            if csv_output:
                mcsv.motion_write(sighup=True)

        # If SIGUSR2 trigger a timings output.
        if output.sig_usr2:
            log.info('Manual SIGUSR2 detected.')
            tcsv = timingsCSV(enabled=csv_timings)
            output.sig_usr2 = False

        # if movement is detected trigger recording.
        if movement_flag:
            if mp4.is_open():
                frames_required = post_frames + 1
            else:
                # Update the version number
                mp4.new_filename(version_num)
                writer = mp4.open()
                frames_required = pre_frames + post_frames + 1
                log.info('Opening {name}...'.format(name=mp4.get_filename()))
                exposure_controls = get_exposure()
                if draw_jpg_graph or draw_graph and not recording_flag:
                    recording_flag = graph.put_start_icon()

            if csv_output:
                mcsv.log_motion(movement_level)

        # Send the stop recording icon to the graph 12 frames before end recording,
        if draw_jpg_graph or draw_graph:
            if frames_required == graph.get_icon_size() and recording_flag:
                recording_flag = graph.put_stop_icon()

        if frames_required > 0:
            if movement_peak < int(buffered_movement[-1::]):
                movement_peak = int(buffered_movement[-1::])
                movement_peak_frame = frames_written + pre_frames
                jpg_frame = np.copy(buffer[index])
                # Save YOLO frame.
                if yolo_output:
                    yolo_peak_movement_frame = np.copy(main_frame)

                # Draw a box around the area of movement of the JPG.
                if not box_jpg == 'OFF':
                    if movement_level:
                        c = max(contours, key=cv2.contourArea)
                        bounding_box = cv2.boundingRect(c)
                        box_text = box_jpg.replace('<value>', str(movement_level))
                        jpg_frame = add_box(jpg_frame, bounding_box, box_text, box_rgb, box_thickness, box_font_size)
                        tcsv.log_point('Draw Movement Box on JPG')

            # Write Graph.
            graph.update_frame(int(buffered_movement[-1::]))
            tcsv.log_point('Update Graph Frame')

            # Draw graph
            if draw_graph:
                roi = graph.get_roi(buffered_frame)  # Gets the roi of the buffered frame.
                roi[:] = graph.get_graph()  # Add the graph

            # Display the frame count.
            if display_frame_cnt:
                put_frame_cnt(buffered_frame, frames_written)

            # Draw roi on mp4 file.
            if display_roi and mask_path:
                buffer[index] = draw_roi(mask_img, buffer[index], display_roi_rgb,
                                         display_roi_thickness, display_roi_font_size)

            # Draw a box around the area of movement on MP4.
            if not box == 'OFF' and buffered_movement[-1::] > 1:
                if buffered_movement[-1::]:
                    x, y, w, h = buffered_bounding_rect[index]
                    box_text = box.replace('<value>', str(buffered_movement[-1::]))
                    buffer[index] = add_box(buffer[index], (x, y, w, h),
                                            box_text, box_rgb, box_thickness, box_font_size)
                    tcsv.log_point('Draw Movement Box on MP4')

            frames_required -= 1
            frames_written += 1
            writer.write(buffered_frame)
            tcsv.log_point('Write Video Frame')

            if display:
                display_buffered_frame = resize_img(buffered_frame, (display_image_width, display_image_height))
                cv2.imshow('Recorded Data', display_buffered_frame)
        else:
            if mp4.is_open():
                # journal.write(f'Closing {mp4.get_filename()}')
                # Write Timelapse JPG before any decorations are added to the frame.
                if timelapse_frame_number > 0:
                    write_timelapse_jpg(buffered_frame)

                # Write last frame here.
                if statistics:
                    buffered_frame = add_statistics(buffered_frame)

                if csv_visits_log:
                    visits.write(trigger_point=trigger_point,
                                 trigger_point_base=trigger_point_base,
                                 subtraction_history=subtraction_history,
                                 subtraction_threshold=subtraction_threshold)

                writer.write(buffered_frame)
                mp4.close()
                tcsv.log_point('Close Video ')

                write_jpg(jpg_frame)
                tcsv.log_point('Write JPEG')

                # csv_path = 'Motion/testTrigger.csv'
                csv_path = mp4.get_pathname().replace('mp4', 'csv')
                trigger_csv.write_csv(csv_path)

                # Update the version number ini file and get the next number.
                version_num = version_class.write_version()

                # Run the command to copy over the mp4 file.
                if not command == "None":
                    cmd = command.replace('<MP4>', mp4.get_filename())
                    log.info('Command after replace is:{}'.format(cmd))
                    run_cmd(cmd)
                else:
                    log.info('Command not run')

                # Update peak movement.
                if csv_output:
                    mcsv.motion_write()

                # Save YOLO image.
                if yolo_output:
                    yolo_peak_movement_frame = flip_image(yolo_peak_movement_frame, image_horizontal_flip,
                                                          image_vertical_flip)
                    write_yolo_jpg(yolo_peak_movement_frame)
                    tcsv.log_point('Write YOLO')

                # Reset flags.
                movement_peak = 0
                frames_written = 0
                movement_frame_cnt = 0

                # Display recorded image.
                if display:
                    cv2.destroyWindow('Recorded Data')

    # Closing down.
    picam2.close()
    log.info('Closing camera...')

    if display:
        cv2.destroyAllWindows()

    if mp4.is_open():
        log.info('Close open MP4 file.')
        mp4.close()

    log.info('Exit Motion.')
    sys.exit(0)
