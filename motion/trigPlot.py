import argparse
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
import socket

parser = argparse.ArgumentParser(description="Report Movement")
parser.add_argument('--days', type=int, default=0, help="Enter the number of days to report.")
parser.add_argument('--hours', type=int, default=0, help="Enter the number of hours to report.")
parser.add_argument('--minutes', type=int, default=0, help="Enter the number of minutes to report.")
parser.add_argument('--title', default="Latest Movement", help="Enter the Title of the report.")
parser.add_argument('--filename', default="trigPlot",
                    help="Enter the output filename, an extension of png will be added.")

args = parser.parse_args()
DAYS = args.days
HOURS = args.hours
MINUTES = args.minutes

title = args.title
filename = args.filename


def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()


data = pd.read_csv('peakMovement.csv')
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

end_date = data['Timestamp'].max()
start_date = end_date - pd.Timedelta(days=DAYS, hours=HOURS, minutes=MINUTES)
data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]

data['Timestamp_idx'] = pd.to_datetime(data['Timestamp'])
data.set_index("Timestamp_idx", inplace=True)
last_ts = data.index[-1]

plt.style.use("seaborn-v0_8-whitegrid")

fig, (ax1, ax2) = plt.subplots(2, sharex=True)

time = data['Timestamp']

st = int(data['Subtraction Threshold'].iloc[-1])
sh = int(data['Subtraction History'].iloc[-1])
tp = int(data['Trigger Point'].iloc[-1])
tpb = int(data['Trigger Point Base'].iloc[-1])
mhw = int(data['Movement History Window'].iloc[-1])
mha = int(data['Movement History Age'].iloc[-1])
ylim = int(data['Trigger Point'].iloc[-1] * 3)
data.loc[data['Trigger Value'] >= ylim, 'Trigger Value'] = ylim
data['Trigger Value'] = data['Trigger Value'].replace(0, np.nan)

if os.name == 'nt':
    ax1.set_title(f'Windows - {title}')
else:
    ax1.set_title(f'{get_host_name()} - {title}')

ax1.plot(time, data['Highest Peak'],
         color='Purple',
         alpha=0.5,
         label='Highest Peak Movement'
         )

ax1.plot(time, data['Trigger Point'],
         color='Green',
         alpha=0.5,
         label=f'Trigger Point {tp}'
         )

ax1.plot(time, data['Trigger Point Base'],
         color='Red',
         alpha=0.5,
         label=f'Trigger Point Base {tpb}'
         )

ax1.plot(time, data['Movement History Window'],
         color='Blue',
         alpha=0.5,
         label=f'Movement History Window {mhw}'
         )

ax1.plot(time, data['Movement History Age'],
         color='Orange',
         alpha=0.5,
         label=f'Movement History Age {mha}'
         )

ax1.set_ylim([0, ylim])

if os.name == 'nt':
    ax2.set_title(f'Windows - {title}')
else:
    ax2.set_title(f'{get_host_name()} - {title}')

ax2.plot(time, data['Average'],
         color='deepskyblue',
         alpha=0.5,
         label='Average Peak Movement'
         )

ax2.plot(time, data['Variable Trigger Point'],
         color='Green',
         alpha=0.5,
         label='Variable Trigger Point'
         )

ax2.plot(time, data['Variable Trigger Point Base'],
         color='Red',
         alpha=0.5,
         label='Variable Trigger Point Base'
         )

ax2.scatter(time, data['Trigger Value'], alpha=0.5, color='Black')

ax2.set_ylim([0, ylim])

plt.gcf().autofmt_xdate()
plt.gcf().autofmt_xdate()
plt.ylabel('Movement')
ax1.legend(loc='best')
ax2.legend(loc='best')

plt.savefig(f'{filename}.png')

if os.name == 'nt':
    plt.show()
