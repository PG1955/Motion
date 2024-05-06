from matplotlib import pyplot as plt
from temperaturePlot import TemperaturePlot
import numpy as np

# plt.rcParams["figure.figsize"] = (5.5,3)
# plt.rcParams["figure.dpi"] = 72*3

fig, ax = plt.subplots()
p = TemperaturePlot()
p.scatter([.25, .5, .75], [.3, .4, .5], s=[800, 1200, 1600], temp=[28, 39, 35], color="C3",
          ax=ax, transform=ax.transAxes)

plt.show()

np.random.seed(42)
fig, ax = plt.subplots()
n = 42
x = np.linspace(0, 100, n)
y = np.cumsum(np.random.randn(n)) + 5

ax.plot(x, y, color="darkgrey", lw=2.5)

p = TemperaturePlot()
p.scatter(x[::4], y[::4] + 3, s=300, temp=y[::4], c=y[::4], edgecolor="k", cmap="RdYlBu_r")

ax.set_ylim(-6, 18)
plt.show()
