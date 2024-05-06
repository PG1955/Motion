"""
Plot shows the number of daily visits.
The yaxis is limited to the average plus 20%.
v1.2 03/05/2023 Add average limit to the y-axis.
"""
import socket

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

__author__ = "Peter Goodgame"
__name__ = "visitsPlot"
__version__ = "v1.2"

# Print Version data.
print(f'Program name: {__name__} version {__version__} ')


def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()


# Read and prepare the data.
df = pd.read_csv('visits.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Filter data on date
df = df.loc[(df['Timestamp'] >= '2023-04-17')]

# Add a visit column.
df['Visit'] = 1

# Calculate and sum up the values for reporting, then merge and build the report data.
tots = df.groupby([df['Timestamp'].dt.date]).count()[['Visit']]
tp = df.groupby([df['Timestamp'].dt.date]).max()[['Trigger Point']]
tpb = df.groupby([df['Timestamp'].dt.date]).max()[['Trigger Point Base']]

data = tots.merge(
    tp, left_on='Timestamp', right_on='Timestamp').merge(
    tpb, left_on='Timestamp', right_on='Timestamp')

# Build the Plot.
plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots()
tp = int(data['Trigger Point'].iloc[-1])
tpb = int(data['Trigger Point Base'].iloc[-1])
ylim = int(data['Visit'].mean() * 1.5)

# ax.plot(data['Visit'])
ax.bar(data.index, data['Visit'])

ax.plot(data['Trigger Point'],
        color='Green',
        alpha=0.5,
        label=f'Trigger point {tp}'
        )

ax.plot(data['Trigger Point Base'],
        color='yellow',
        alpha=0.5,
        label=f'Trigger Point Base {tpb}'
        )

plt.gcf().autofmt_xdate()
date_format = mdates.DateFormatter('%m %d')
axes = plt.gca()
axes.xaxis.set_major_formatter(date_format)
axes.set_ylim([0, ylim])
plt.gcf().autofmt_xdate()
plt.legend(loc='best')

# Labels and title.
plt.xlabel('Date')
plt.ylabel('Number of Visits')
if os.name == 'nt':
    plt.title('Windows - Visits')
else:
    plt.title(get_host_name() + ' - Visits')

# Save the chart as a png file.
plt.savefig('visits.png')

if os.name == 'nt':
    plt.show()
