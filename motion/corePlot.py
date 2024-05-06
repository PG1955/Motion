import argparse
import socket

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
import os

df = pd.read_csv('coredata.csv')

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Timestamp_idx'] = pd.to_datetime(df['Timestamp'])
df.set_index("Timestamp_idx", inplace=True)

# Use this if the timestamp is the index of the DataFrame
last_ts = df.index[-1]
first_ts = last_ts - pd.Timedelta(24, 'hours')
df = df[df.index >= first_ts]

plt.style.use("seaborn-v0_8-whitegrid")


def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()


fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(11, 8), sharex=True)

time = df['Timestamp']
plt.gcf().autofmt_xdate()
date_format = mpl_dates.DateFormatter('%a %H %M')
plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()

if os.name == 'nt':
    ax1.set_title(f'Windows - Core Data')
else:
    ax1.set_title(f'{get_host_name()} - Core Data')

ax1.plot(time, df['arm_freq'],
         # color='Purple',
         alpha=0.5,
         label='arm_freq'
         )

ax1.plot(time, df['arm_freq_min'],
         # color='Purple',
         alpha=0.5,
         label='arm_freq_min'
         )

ax1.plot(time, df['core_freq'],
         # color='Purple',
         alpha=0.5,
         label='core_freq'
         )

ax1.plot(time, df['core_freq_min'],
         # color='Purple',
         alpha=0.5,
         label='core_freq_min'
         )

ax1.plot(time, df['gpu_freq'],
         color='yellow',
         alpha=0.5,
         label='gpu_freq'
         )

ax1.plot(time, df['gpu_freq_min'],
         # color='Purple',
         alpha=0.5,
         label='gpu_freq_min'
         )

ax1.set_title("Frequencies")
ax1.legend(loc='best')

ax2.plot(time, df['core: volt'],
         color='Red',
         alpha=0.5,
         label='core: volt'
         )

ax2.plot(time, df['sdram_c: volt'],
         color='Green',
         alpha=0.5,
         label='sdram_c: volt'
         )

ax2.plot(time, df['sdram_p: volt'],
         color='Blue',
         alpha=0.5,
         label='sdram_p: volt'
         )

ax2.set_title("Voltages")
ax2.legend(loc='best')

ax3.plot(time, df['sdram_freq'],
         color='Orange',
         alpha=0.5,
         label='sdram_freq'
         )
ax3.plot(time, df['arm: frequency(48)'],
         color='Purple',
         alpha=0.5,
         label='arm: frequency(48)'
         )
ax3.plot(time, df['core: frequency(1)'],
         color='Red',
         alpha=0.5,
         label='core: frequency(1)'
         )
ax3.plot(time, df['h264: frequency(28)'],
         color='Blue',
         alpha=0.5,
         label='h264: frequency(28)'
         )
ax3.plot(time, df['isp: frequency(45)'],
         color='Green',
         alpha=0.5,
         label='isp: frequency(45)'
         )

ax3.plot(time, df['v3d: frequency(46)'],
         color='Orange',
         alpha=0.5,
         label='v3d: frequency(46))'
         )

ax3.set_title("Core Frequencies")
ax3.legend(loc='best')

ax4.plot(time, df['temp'],
         color='Orange',
         alpha=0.5,
         label='temp'
         )

ax4.set_title("Core Temperature")
ax4.legend(loc='best')

# ,,throttled

plt.savefig('coredata.png')

if os.name == 'nt':
    plt.show()
