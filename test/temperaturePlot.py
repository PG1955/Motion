import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath


class TemperaturePlot():

    @staticmethod
    def get_hull():
        verts1 = np.array([[0, -128], [70, -128], [128, -70], [128, 0],
                           [128, 32.5], [115.8, 61.5], [96, 84.6], [96, 288],
                           [96, 341], [53, 384], [0, 384]])
        verts2 = verts1[:-1, :] * np.array([-1, 1])
        codes1 = [1, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4]
        verts3 = np.array([[0, -80], [44, -80], [80, -44], [80, 0],
                           [80, 34.3], [60.7, 52], [48, 66.5], [48, 288],
                           [48, 314], [26.5, 336], [0, 336]])
        verts4 = verts3[:-1, :] * np.array([-1, 1])
        verts = np.concatenate((verts1, verts2[::-1], verts4, verts3[::-1]))
        codes = codes1 + codes1[::-1][:-1]
        return mpath.Path(verts / 256., codes + codes)

    @staticmethod
    def get_mercury(s=1):
        a = 0;
        b = 64;
        c = 35
        d = 320 - b
        e = (1 - s) * d
        verts1 = np.array([[a, -b], [c, -b], [b, -c], [b, a], [b, c], [c, b], [a, b]])
        verts2 = verts1[:-1, :] * np.array([-1, 1])
        verts3 = np.array([[0, 0], [32, 0], [32, 288 - e], [32, 305 - e],
                           [17.5, 320 - e], [0, 320 - e]])
        verts4 = verts3[:-1, :] * np.array([-1, 1])
        codes = [1] + [4] * 12 + [1, 2, 2, 4, 4, 4, 4, 4, 4, 2, 2]
        verts = np.concatenate((verts1, verts2[::-1], verts3, verts4[::-1]))
        return mpath.Path(verts / 256., codes)

    def scatter(self, x, y, temp=1, tempnorm=None, ax=None, **kwargs):
        self.ax = ax or plt.gca()
        temp = np.atleast_1d(temp)
        ec = kwargs.pop("edgecolor", "black")
        kwargs.update(linewidth=0)
        self.inner = self.ax.scatter(x, y, **kwargs)
        kwargs.update(c=None, facecolor=ec, edgecolor=None, color=None)
        self.outer = self.ax.scatter(x, y, **kwargs)
        self.outer.set_paths([self.get_hull()])
        if not tempnorm:
            mi, ma = np.nanmin(temp), np.nanmax(temp)
            if mi == ma:
                mi = 0
            tempnorm = plt.Normalize(mi, ma)
        ipaths = [self.get_mercury(tempnorm(t)) for t in temp]
        self.inner.set_paths(ipaths)


plt.rcParams["figure.figsize"] = (5.5,3)
plt.rcParams["figure.dpi"] = 72*3

fig, ax = plt.subplots()
p = TemperaturePlot()
p.scatter([.25,.5,.75], [.3,.4,.5], s=[800,1200,1600], temp=[28,39,35], color="C3",
          ax=ax, transform=ax.transAxes)

plt.show()