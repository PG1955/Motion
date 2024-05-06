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
    return str(timedelta(seconds=int(seconds)))


# Sample data with HH:MM:SS format: Replace this with your actual data
data = {
    'Timestamp': [
        '2024-04-18 10:00:00', '2024-04-19 10:30:00', '2024-04-19 11:00:00',
        '2024-04-20 10:00:00', '2024-04-20 10:30:00', '2024-04-20 11:00:00',
        '2024-04-20 11:30:00', '2024-04-20 12:00:00'
    ],
    'Duration': ['0:05:00', '0:10:00', '0:15:00', '0:20:00', '0:25:00', '0:15:00', '0:00:45', '0:25:00']
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert Timestamps to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Extract date and hour
df['Date'] = df['Timestamp'].dt.date
df['Hour'] = df['Timestamp'].dt.hour

# Convert Duration from HH:MM:SS to seconds
df['Duration'] = df['Duration'].apply(convert_to_seconds)

# Group by date and hour, sum durations
grouped = df.groupby(['Date', 'Hour'])['Duration'].sum().reset_index()

# Plot
plt.figure(figsize=(10, 6))
plt.bar(grouped['Date'].astype(str) + ' ' + grouped['Hour'].astype(str), grouped['Duration'])

# Labeling
plt.xlabel('Date and Hour')
plt.ylabel('Duration (HH:MM:SS)')
plt.title('Duration by Date and Hour')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Apply custom formatter to the Y-axis
plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

# Display the plot
plt.tight_layout()
plt.show()
