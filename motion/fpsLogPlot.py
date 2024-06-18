"""
Plot shows the frames per second recorded.
"""

import socket
import argparse
import pandas as pd
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
import os

__author__ = "Peter Goodgame"
__name__ = "fpsLogPlot"
__version__ = "v1.2"

# plt.style.use('seaborn-v0_8-whitegrid')

def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()

# Print Version data.
print(f'Program name: {__name__} version {__version__} ')

parser = argparse.ArgumentParser(description="Frames Per Second Report")
parser.add_argument('--days', type=int, default=0, help="Enter the number of days to report.")
parser.add_argument('--hours', type=int, default=0, help="Enter the number of hours to report.")
parser.add_argument('--title', default="Frames Per Second", help="Enter the Title of the report.")
parser.add_argument('--filename', default="fps",
                    help="Enter the output filename, an extension of png will be added.")
parser.add_argument('--dir', default=".",
                    help="Enter the output directory, the default is the current directory")

args = parser.parse_args()
DAYS = args.days
HOURS = args.hours
TITLE = args.title
FILENAME = args.filename
DIR = args.dir

if (DAYS + HOURS) == 0:
    DAYS = 28

# df = pd.read_csv('./fps.csv')
# df = df.tail(800)

# Read and prepare the data.
df = pd.read_csv('fps.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.sort_values('Timestamp', inplace=True)

# Limit days data.
end_date = df['Timestamp'].max()
start_date = end_date - pd.Timedelta(days=DAYS, hours=HOURS)
df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# df['Timestamp'] = pd.to_datetime(df['Timestamp'])
# df.sort_values('Timestamp', inplace=True)

time = df['Timestamp']
plt.gcf().autofmt_xdate()
date_format = mpl_dates.DateFormatter('%a %H:%M')
# date_format = mpl_dates.DateFormatter('%H:%M')
plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()

FPS = int(df['Actual Frames Per Second'].iloc[-1])
SHR = int(df['Shared Memory Size'].iloc[-1])
RES = int(df['Resident Memory Size'].iloc[-1])
VRT = int(df['Virtual Memory Size'].iloc[-1])

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, figsize=(6, 7), sharex=True)

ax1.plot(time, df['Expected Frames Per Second'],
         color='Red',
         label='FPS'
         )

ax1.plot(time, df['Actual Frames Per Second'],
         color='Green',
         label='FPS'
         )

ax1.legend(loc='best')

ax2.plot(time, df["Shared Memory Size"],
         color='Blue',
         label='Shared'
         )

ax3.plot(time, df["Resident Memory Size"],
         color='Red',
         label='Shared'
         )

ax4.plot(time, df["Virtual Memory Size"],
         color='Orange',
         label='Virtual'
         )

# ax2.legend(loc='best')


plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()

if os.name == 'nt':
    ax1.set_title('Windows - Frames Per Second')
    ax2.set_title('Shared Process Memory')
    ax3.set_title('Resident Process Memory')
    ax4.set_title('Virtual Process Memory')
else:
    ax1.set_title(get_host_name() + ' - FPS is currently ' + str(FPS))
    ax2.set_title(get_host_name() + ' - Shared Process Memory is currently ' + str(SHR))
    ax3.set_title(get_host_name() + ' - Resident Process Memory is currently ' + str(RES))
    ax4.set_title(get_host_name() + ' - Virtual Process Memory is currently ' + str(VRT))

# Save the chart as a png file.
# Ensure output dir exists.
if not os.path.exists(DIR):
    os.mkdir(DIR)

# Save report.
filename = f'{FILENAME}.png'
output = os.path.join(DIR,filename)
print(f'Save output to {output}')
plt.savefig(output)

if os.name == 'nt':
    plt.show()
