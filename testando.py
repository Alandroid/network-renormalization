from matplotlib import colors, pyplot as plt
import numpy as np


cmap = plt.get_cmap("seismic")
cmap_list = []

for i in range(100):
    if not i%15:
        cmap_list.append(cmap(i/100))
    #print(cmap(i/100))


fig, ax = plt.subplots(6, sharex=True)

x = np.linspace(0, 10, 500)

for i in range(1, 6):
    y = i*x
    ax[i].plot(x, y, color = cmap_list[i], linewidth=5)

fig.savefig("cores.pdf")
plt.close()