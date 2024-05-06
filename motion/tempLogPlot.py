import argparse
import socket

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
import os

parser = argparse.ArgumentParser(description="Report Temperatures")
parser.add_argument('--days', type=int, default=0, help="Enter the number of days to report.")
parser.add_argument('--hours', type=int, default=0, help="Enter the number of hours to report.")
parser.add_argument('--title', default="temperatures", help="Enter the title.")
parser.add_argument('--filename', default="temperatures",
                    help="Enter the output filename, an extension of png will be added.")

args = parser.parse_args()
DAYS = args.days
HOURS = args.hours
TITLE = args.title
FILENAME = args.filename

if (DAYS + HOURS) == 0:
    DAYS = 365

plt.style.use('seaborn-v0_8-whitegrid')


def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()


data = pd.read_csv('./temperatures.csv')


data['Timestamp'] = pd.to_datetime(data['Timestamp'])
# Limit the data reported.
end_date = data['Timestamp'].max()
start_date = end_date - pd.Timedelta(days=DAYS, hours=HOURS)
data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]
data.sort_values('Timestamp', inplace=True)
time = data['Timestamp']
plt.gcf().autofmt_xdate()
date_format = mpl_dates.DateFormatter('%a %H:%M')
plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()
C = int(data['Centigrade'].iloc[-1])
H = int(data['Humidity'].iloc[-1])
DEG = u'\N{DEGREE SIGN}'

fig, (ax1, ax2) = plt.subplots(2, sharex=True)

if os.name == 'nt':
    ax1.set_title(f'Windows {TITLE} - temperature currently {str(C)}{DEG}C')
else:
    ax1.set_title(f'{get_host_name()} {TITLE} - temperature currently {str(C)}{DEG}C')

ax1.plot(time, data['Centigrade'],
         color='Black',
         label='Centigrade'
         )

ax1.legend(loc='best')

if os.name == 'nt':
    ax2.set_title(f'Windows {TITLE} - humidity currently {str(H)}%')
else:
    ax2.set_title(f'{get_host_name()} - {TITLE} humidity currently {str(H)}%')

ax2.plot(time, data['Humidity'], color='Blue', label='Humidity')

plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()

ax2.legend(loc='best')

plt.savefig(f'{FILENAME}.png')
# plt.savefig('temperatures.png')

if os.name == 'nt':
    plt.show()
