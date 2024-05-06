import socket

import pandas as pd
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
import os

plt.style.use('seaborn-v0_8-whitegrid')

def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()

data = pd.read_csv('./fps.csv')
data = data.tail(800)

data['Timestamp'] = pd.to_datetime(data['Timestamp'])
data.sort_values('Timestamp', inplace=True)
time = data['Timestamp']
plt.gcf().autofmt_xdate()
date_format = mpl_dates.DateFormatter('%a %H:%M')
# date_format = mpl_dates.DateFormatter('%H:%M')
plt.gca().xaxis.set_major_formatter(date_format)
plt.gcf().autofmt_xdate()
FPS = int(data['Actual Frames Per Second'].iloc[-1])
SHR = int(data['Shared Memory Size'].iloc[-1])
RES = int(data['Resident Memory Size'].iloc[-1])
VRT = int(data['Virtual Memory Size'].iloc[-1])

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, figsize=(6, 7), sharex=True)

ax1.plot(time, data['Expected Frames Per Second'],
         color='Red',
         label='FPS'
         )

ax1.plot(time, data['Actual Frames Per Second'],
         color='Green',
         label='FPS'
         )

ax1.legend(loc='best')

ax2.plot(time, data["Shared Memory Size"],
         color='Blue',
         label='Shared'
         )

ax3.plot(time, data["Resident Memory Size"],
         color='Red',
         label='Shared'
         )

ax4.plot(time, data["Virtual Memory Size"],
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

plt.savefig('fps.png')

if os.name == 'nt':
    plt.show()
