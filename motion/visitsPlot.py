"""
Plot shows the number of daily visits.
The yaxis is limited to the average plus 20%.
v1.2 03/05/2023 Add average limit to the y-axis.
v1.3 07/05/2024 Add selection.
"""
import argparse
import socket
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

__author__ = "Peter Goodgame"
__name__ = "visitsPlot"
__version__ = "v1.3"

# Print Version data.
print(f'Program name: {__name__} version {__version__} ')

parser = argparse.ArgumentParser(description="Daily Visits")
parser.add_argument('--days', type=int, default=10, help="Enter the number of days to report.")
parser.add_argument('--title', default="Daily Visits", help="Enter the Title of the report.")
parser.add_argument('--filename', default="visits",
                    help="Enter the output filename, an extension of png will be added.")

args = parser.parse_args()
DAYS = args.days
TITLE = args.title
FILENAME = args.filename


def get_host_name():
    return socket.gethostname().split('.')[0].capitalize()


# Read and prepare the data.
df = pd.read_csv('visits.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.sort_values('Timestamp', inplace=True)

# Filter data
end_date = df['Timestamp'].max()
start_date = end_date - pd.Timedelta(days=DAYS)
df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]

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
y_limit = int(data['Visit'].mean() * 1.5)

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
date_format = mdates.DateFormatter('%b %d')
axes = plt.gca()
axes.xaxis.set_major_formatter(date_format)
axes.set_ylim([0, y_limit])
plt.gcf().autofmt_xdate()
plt.legend(loc='best')

# Labels and title.
plt.xlabel('Date')
plt.ylabel('Number of Visits')
if os.name == 'nt':
    plt.title(f'Windows - {TITLE}')
else:
    plt.title(f'{get_host_name()} - {TITLE}')

# plt.title(TITLE)

# Save the chart as a png file.
plt.savefig(f'{FILENAME}.png')

if os.name == 'nt':
    plt.show()
