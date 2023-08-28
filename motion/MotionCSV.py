import csv
from datetime import datetime
from os.path import exists


class MotionCSV:
    fields = ["Timestamp", "Peak Movement", "Trigger point", "Frames Checked", "Weighted alpha"]
    filename = "peekMovement.csv"

    def __init__(self):
        return

    def write(self, peak, triggerPoint, framesChecked, weightedAlpha):
        # writing to csv file
        if not exists(MotionCSV.filename):
            self.create()

        with open(MotionCSV.filename, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=MotionCSV.fields)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({"Timestamp": timestamp,
                             "Peak Movement": peak,
                             "Trigger point": triggerPoint,
                             "Frames Checked": framesChecked,
                             "Weighted alpha": weightedAlpha})

    def create(self):
        # writing to csv file
        with open(MotionCSV.filename, 'w', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=MotionCSV.fields)
            # writing headers (field names)
            writer.writeheader()


