import argparse
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description="Report Trigger Event")
parser.add_argument('--filename', default="Motion/triggerPlot.csv",
                    help="Enter the output filename, an extension of png will be added.")

args = parser.parse_args()
filename = args.filename
df = pd.read_csv(filename)

tp = int(df['Trigger Point'].iloc[-1])
tpb = int(df['Trigger Point Base'].iloc[-1])
etp = int(df['Event Trigger Point'].iloc[-1])
etpb = int(df['Event Trigger Point Base'].iloc[-1])
mw = int(df['Movement Window'].iloc[-1])
mwa = int(df['Movement Window Age'].iloc[-1])
half_way = round(len(df) / 2)

fig, (ax1) = plt.subplots(1, sharex=True)

if os.name == 'nt':
    ax1.set_title(f'Windows - Trigger Event')
else:
    ax1.set_title(f'{str(os.uname()[1])} - Trigger Event')

ax1.plot(df['Movement Level'],
         color='Black',
         alpha=0.5,
         label='Mvmt Level'
         )

ax1.plot(df['Event Trigger Point'],
         color='Green',
         alpha=0.5,
         label=f'Event TP {etp}'
         )

ax1.plot(df['Event Trigger Point Base'],
         color='Red',
         alpha=0.5,
         label=f'Event TP Base {etpb}'
         )


if mw > 0:
    ax1.plot(df['Movement Window'],
             color='Blue',
             alpha=0.5,
             label=f'Mvmt Win {mw}'
             )

if mwa > 0:
    ax1.plot(df['Movement Window Age'],
             color='Orange',
             alpha=0.5,
             label=f'Mvmt Win Age {mwa}'
             )

ax1.plot(df['Trigger Point'],
         color='White',
         alpha=0.5,
         label=f'TP {tp}'
         )

ax1.plot(df['Trigger Point Base'],
         color='White',
         alpha=0.5,
         label=f'TPBase {tpb}'
         )


ax1.axvline(x=half_way)


ax1.legend(loc='best')

csv_path = filename.replace('csv', 'png')
plt.savefig(csv_path)

if os.name == 'nt':
    plt.show()
