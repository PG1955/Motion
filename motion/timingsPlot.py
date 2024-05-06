import os

import pandas as pd
from matplotlib import pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")

data = pd.read_csv('timings.csv')

data.groupby('Point')['Milliseconds'].mean().plot(kind='barh')
averages = data.groupby('Point')['Milliseconds'].mean().astype(int)
averages.to_csv("timing_summary.csv", index=True)

plt.yticks(rotation = 70)


plt.savefig('timings.png')

if os.name == 'nt':
    plt.show()

# Plot a bar chart
# data.plot.barh(x='Point', y='Milliseconds',
#              title='Timings', color='green')
#
# plt.show()
