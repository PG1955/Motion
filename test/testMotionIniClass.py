import configparser
import os


class MotionINI:
    def __init__(self):
        """
        This class handles the motion.ini file.
        """
        self.filename = 'motion.ini'
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.sections = ['DISPLAY', 'CAMERA', 'MP4', 'OUTPUT', 'STATISTICS', 'GRAPH', 'MOTION', 'ROI', 'BOX', 'DATE']


    def write(self):
        """Write a new motion.ini file."""
        for section in sorted(self.sections):
            self.config.add_section(section)

        self.config.set('MP4', '# Set the frame rates and the number of frames to establish a stable pattern.')
        self.config.set('MP4', '; image_record_fps', '30')
        self.config.set('MP4', '; image_playback_fps', '30')
        self.config.set('MP4', '; stabilise', '40')

        self.config.set('MOTION', '# Set the level at which motion is started and ends.')
        self.config.set('MOTION', 'trigger_point', '40')
        self.config.set('MOTION', 'trigger_point_base', '10')
        self.config.set('MOTION', '# Use movement window and age to smooth out motion triggering.')
        self.config.set('MOTION', '; movement_window', '30')
        self.config.set('MOTION', '; movement_window_age', '10')
        self.config.set('MOTION', '# Set trigger_point_csv_window to output analysis of the trigger points')
        self.config.set('MOTION', '; trigger_point_csv_window', '50')
        self.config.set('MOTION', '# MOG2 Settings.')
        self.config.set('MOTION', '; subtraction_history', '100')
        self.config.set('MOTION', '; subtraction_threshold', '40')

        self.config.set('CAMERA', '# Camera Settings.')
        self.config.set('CAMERA', '; camera_tuning_file', 'imx708.json')
        self.config.set('CAMERA', '; camera_controls', '{"AeMeteringMode": controls.AeMeteringModeEnum.Spot}')
        self.config.set('CAMERA', 'lores_width', '640')
        self.config.set('CAMERA', 'lores_height', '360')
        self.config.set('CAMERA', 'main_width', '640')
        self.config.set('CAMERA', 'main_height', '360')
        self.config.set('CAMERA', '; image_horizontal_flip', 'on')
        self.config.set('CAMERA', '; image_vertical_flip', 'on')
        self.config.set('CAMERA', '; zoom_factor', '1.3')

        self.config.set('DISPLAY', 'display', 'on')
        self.config.set('DISPLAY', 'display_image_width', '640')
        self.config.set('DISPLAY', 'display_image_height', '360')

        self.config.set('OUTPUT', '# Output parameters')
        self.config.set('OUTPUT', '# Execute this after completing output <MP4> will be the mp4 file path.')
        self.config.set('OUTPUT', '; command', 'ln -s /home/pi/Motion/<MP4> /var/www/html/<MP4>')
        self.config.set('OUTPUT', 'output_dir', 'Motion')
        self.config.set('OUTPUT', '# Number of extra frames before and after the event.')
        self.config.set('OUTPUT', '; pre_frames', '20')
        self.config.set('OUTPUT', '; post_frames', '80')
        self.config.set('OUTPUT', 'timelapse_frame_number', '17')
        self.config.set('OUTPUT', '; csv_output', 'on')

        self.config.set('OUTPUT', '; display_frame_cnt', 'on')
        self.config.set('OUTPUT', '; csv_timings', 'on')
        self.config.set('OUTPUT', '; yolo_output', 'on')
        self.config.set('OUTPUT', '; csv_visits_log', 'on')
        self.config.set('OUTPUT', '; csv_output', 'off')
        self.config.set('OUTPUT', '; csv_timings', 'off')

        self.config.set('GRAPH', '# Output a graph on MP4 of jpg if set to on and off is the default.')
        self.config.set('GRAPH', '; draw_graph', 'on')
        self.config.set('GRAPH', 'draw_jpg_graph', 'on')

        self.config.set('ROI', '# Define the area of interest.')
        self.config.set('ROI', '; mask_path', 'Motion/props/mask.jpg')
        self.config.set('ROI', 'display_roi', 'on')
        self.config.set('ROI', 'display_roi_jpg', 'on')
        self.config.set('ROI', 'display_roi_thickness', '1')
        self.config.set('ROI', 'display_roi_font_size', '0.7')
        self.config.set('ROI', 'display_roi_rgb', '255, 0, 0')

        self.config.set('BOX', '# Draw a box around the area of movement. <value> is the movement level.')
        self.config.set('BOX', '; box', 'Movement <value>')
        self.config.set('BOX', 'box_jpg', 'Movement <value>')
        self.config.set('BOX', 'box_thickness', '1')
        self.config.set('BOX', 'box_font_size', '0.3')
        self.config.set('BOX', 'box_rgb', '254, 228, 64')
        self.config.set('BOX', 'box_jpg_rgb', '254, 228, 64')

        self.config.set('STATISTICS', '# Display statistics.')
        self.config.set('STATISTICS', '; statistics', 'on')
        self.config.set('STATISTICS', 'statistics_jpg', 'on')
        self.config.set('STATISTICS', 'statistics_font_scale', '0.4')
        self.config.set('STATISTICS', 'statistics_font_thickness', '1')
        self.config.set('STATISTICS', 'statistics_rgb', '0, 255, 0')
        self.config.set('STATISTICS', 'print_fps', 'on')

        self.config.set('DATE', '# Print date.')
        self.config.set('DATE', 'date_position', 'top')
        self.config.set('DATE', 'date_font_scale', '0.4')
        self.config.set('DATE', 'date_font_thickness', '1')
        self.config.set('DATE', 'date_rgb', '4, 231, 98')

        with open(self.filename, 'w') as inifile:
            self.config.write(inifile)

    def get_config(self):
        """Return the current motion config file."""
        return self.config

    def read_config(self):
        """Read the motion.ini config file.
        If the file does not exist one will be created with default values."""
        if not os.path.exists(self.filename):
            self.write()
        self.config.read(self.filename)
        return self.config

    def get_parameter(self, section, name, default):
        """Get a parameter from the motion.ini file."""
        try:
            # value = self.config.get('DATE', name)
            value = self.config.get(section, name)
            print('{} {}: {}'.format(section, name, value))
        except:
            value = default
        if isinstance(value, str):
            if value.lower() == 'on':
                value = True
            elif value.lower() == 'off':
                value = False
        return value

    def remove(self):
        """Deletes the current motion.ini file. Use with caution."""
        if os.path.exists(self.filename):
            os.remove(self.filename)


mini = MotionINI()
mini.remove()
mini.read_config()

date_position = mini.get_parameter('DATE', 'date_position', 'none')
print(date_position)

# box = motion_ini.get('BOX', 'box', fallback=False)
# box_jpg = motion_ini.get('BOX', 'box_jpg', fallback=False)
# box_thickness = motion_ini.get('BOX', 'box_thickness', fallback=1)
# box_font_size = motion_ini.get('BOX', 'box_font_size', fallback=0.3)
# box_rgb = motion_ini.get('BOX', 'box_rgb', fallback='0,255,0')
# box_jpg_rgb = motion_ini.get('BOX', 'box_jpg_rgb', fallback='0,255,0')


# print(f'box:{box}')
