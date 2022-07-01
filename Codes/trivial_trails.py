import matplotlib.pyplot as plt
import numpy as np
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

'''x = np.linspace(-2, 2, 200)

duration = 2

fig: plt.Figure
ax: plt.Axes
fig, ax = plt.subplots()
i = 0


def make_frame(t):
    global i
    i += 1
    ax.clear()
    ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
    ax.set_ylim(-1.5, 2.5)
    ax.set_title(str(t))
    return mplfig_to_npimage(fig)


animation = VideoClip(make_frame, duration=duration)
animation.write_videofile('C:\\Users\\Kunko\\Desktop\\trail.mp4', fps=20)
'''