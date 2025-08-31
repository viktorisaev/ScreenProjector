import numpy as np
import matplotlib.pyplot as plt


# global setup
FOV = 90  # degrees
ScreenWidth = 2
PlaneWidth = 1.8  # width of the plane at distance = 1

# derived saetup
focal_length = ScreenWidth / (2 * np.tan(np.deg2rad(FOV) / 2))
HalfScreenWidth = ScreenWidth / 2
HalfPlaneWidth = PlaneWidth / 2


def drawLine(p1, p2, color='green', linestyle='--'):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linestyle=linestyle)

def drawPoint(p, color='green'):
    ax.plot(p[0], p[1], marker='o', markersize=5, markerfacecolor='none', markeredgecolor=color, markeredgewidth=2)

# Create a figure and axis
fig = plt.figure(figsize=(10, 10), dpi=100)  # 10×6 inches at 100 DPI → 1000×600 pixels
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)

# Initial line from (0,0) to (0,0)
#line = ax.plot([0, 0], [0, 0], color='red')

def drawCurrent(x,y):
    ax.clear()
    ax.set_xlim(-HalfScreenWidth, HalfScreenWidth)
    ax.set_ylim(-focal_length, HalfPlaneWidth)        
    plt.grid(True)
    plt.title("focal_length = {:.2f}".format(focal_length))
    # screen
    drawLine([-HalfScreenWidth,0], [HalfScreenWidth,0], color='blue', linestyle='-')
    #plane
    planeOrig = [[-PlaneWidth/2, 0], [PlaneWidth/2, 0]] ## coordinates of the plane in local plane space
    drawLine(planeOrig[0], planeOrig[1], color='red', linestyle='-')
    drawPoint(planeOrig[0], color='red')
    drawPoint(planeOrig[1], color='red')

    drawLine([0,-focal_length], [x,y])
    drawPoint([x,y])
    fig.canvas.draw_idle()         # Redraw efficiently


# Event handler for mouse movement
def on_mouse_move(event):
    if event.inaxes == ax:  # Only update if inside the plot
        drawCurrent(event.xdata, event.ydata)
# Connect the event
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

# initial draw
drawCurrent(0,0)
plt.show()
