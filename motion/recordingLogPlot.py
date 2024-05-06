import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.ticker import FuncFormatter


# Function to convert HH:MM:SS to seconds
def convert_to_seconds(hms_str):
    h, m, s = map(int, hms_str.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s).total_seconds()


# Function to format seconds to HH:MM:SS
def format_hms(seconds):
    return str(timedelta(seconds=seconds))


# Custom formatter for the Y-axis
def y_axis_formatter(seconds, pos):
    return str(timedelta(days=0, hours=0, minutes=0, seconds=int(seconds)))


parser = argparse.ArgumentParser(description="Recording Times Report")
parser.add_argument('--days', type=int, default=1, help="Enter the number of days to report.")
parser.add_argument('--hours', type=int, default=0, help="Enter the number of hours to report.")
parser.add_argument('--minutes', type=int, default=0, help="Enter the number of minutes to report.")
parser.add_argument('--title', default="Recording Duration by Date and Hour", help="Enter the Title of the report.")
parser.add_argument('--filename', default="recording",
                    help="Enter the output filename, an extension of png will be added.")

args = parser.parse_args()
DAYS = args.days
HOURS = args.hours
MINUTES = args.minutes
TITLE = args.title
FILENAME = args.filename

# Load Data
df = pd.read_csv('recording.csv')

# Convert Timestamps to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

df.sort_values('Timestamp', inplace=True)

# Filter data
end_date = df['Timestamp'].max()
start_date = end_date - pd.Timedelta(days=DAYS, hours=HOURS, minutes=MINUTES)
df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]

# Add hour to the data frame.
df['Hour'] = df['Timestamp'].dt.hour


# Convert Duration from HH:MM:SS to seconds
df['Duration'] = df['Duration'].apply(convert_to_seconds)

# # Add a timedelta element to the df.
# df['Duration'] = pd.to_timedelta(df['Duration'])

# Extract date and hour
df['Date'] = df['Timestamp'].dt.date
df['Hour'] = df['Timestamp'].dt.hour

# Group by date and hour, sum durations
grouped = df.groupby(['Date', 'Hour'])['Duration'].sum().reset_index()

# Plot
plt.figure(figsize=(10, 6))
plt.bar(grouped['Date'].astype(str) + ' ' + grouped['Hour'].astype(str), grouped['Duration'])

# Labeling
plt.xlabel('Date and Hour')
plt.ylabel('Duration (HH:MM:SS)')
plt.title(TITLE)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Apply custom formatter to the Y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

# Display the plot
plt.tight_layout()

plt.savefig(f'{FILENAME}.png')

if os.name == 'nt':
    # Display the plot
    plt.tight_layout()
    plt.show()

