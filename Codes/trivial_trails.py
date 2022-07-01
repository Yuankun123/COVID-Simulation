"""Trail"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import time
import numpy as np
'''fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_axes([0, 0.05, 1, 0.9])
plt.ion()
for i in range(1000):
    ax.clear()
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_aspect('equal')
    ax.add_patch(patches.Rectangle(xy=(0, 0), width=random.randint(5, 10), height=random.randint(5, 10)))
    plt.show()'''

'''plt.ion()
plt.plot([1.4, 2.5])
plt.title(" Sample interactive plot")

axes = plt.gca()
axes.plot([3.1, 2.2])
plt.pause(1)
'''

x = np.linspace(0, 10 * np.pi, 100)
y = np.sin(x)

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(x, y, 'b-')

for phase in np.linspace(0, 10 * np.pi, 100):
    line1.set_ydata(np.sin(0.5 * x + phase))
    fig.canvas.draw()
    time.sleep(0.1)
