import os
from datetime import datetime
import cv2


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
