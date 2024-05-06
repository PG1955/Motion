import os
from datetime import datetime, timedelta

import pandas as pd

data = pd.read_csv('record_times.csv')

print(data)

data.drop(columns=['Start'], inplace=True)
print(data)

# Save the DataFrame to a CSV file
data.to_csv('recording.csv', index=False)
