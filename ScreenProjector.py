import numpy as np
import matplotlib.pyplot as plt


# global setup
FOV = 90  # degrees
ScreenWidth = 2
HowScale = 3  # how much wider the screen is shown compared to the actual screen width
PlaneWidth = 1.4  # width of the plane at distance = 1

# derived saetup
focal_length = ScreenWidth / (2 * np.tan(np.deg2rad(FOV) / 2))
HalfScreenWidth = ScreenWidth / 2
HalfPlaneWidth = PlaneWidth / 2

planeRotation = 0  # degrees

# drawing

def drawLine(p1, p2, color='green', linestyle='--', linewidth=1):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linestyle=linestyle, linewidth=linewidth)

def drawPoint(p, color='green'):
    ax.plot(p[0], p[1], marker='o', markersize=5, markerfacecolor='none', markeredgecolor=color, markeredgewidth=2)


# math

def createRotationMatrix(angle):
    rad = np.deg2rad(angle)
    c = np.cos(rad)
    s = np.sin(rad)
    return np.array([[c, -s], [s, c]])

def rotatePoint(point, R):
    return R @ point


def createProjectionMatrix2x2():
    return np.array([[focal_length, 0], [0, 1]])

# Create a figure and axis
# Remove 'q' from the quit keymap
plt.rcParams['keymap.quit'] = []  # or set to a different key, e.g., ['ctrl+q']
fig = plt.figure(figsize=(10, 10/HowScale), dpi=100)  # 10×6 inches at 100 DPI → 1000×600 pixels
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)

# Initial line from (0,0) to (0,0)
#line = ax.plot([0, 0], [0, 0], color='red')

mouse = [0,0]

def drawCurrent():
    x = mouse[0]
    y = mouse[1]

    ax.clear()
    ax.set_xlim(-HalfScreenWidth*HowScale, HalfScreenWidth*HowScale)
    ax.set_ylim(-focal_length, HalfPlaneWidth)        
    plt.grid(True)
    plt.title("focal_length = {:.2f}".format(focal_length))
    # screen
    drawLine([-HalfScreenWidth,0], [HalfScreenWidth,0], color='blue', linestyle='-')
    #plane
    planeOrig = [[-PlaneWidth/2, 0], [PlaneWidth/2, 0]] ## coordinates of the plane in local plane space
    R = createRotationMatrix(planeRotation)
    plane = [rotatePoint(planeOrig[0], R), rotatePoint(planeOrig[1], R)]  # rotated plane coordinates
    drawLine(plane[0], plane[1], color='red', linestyle='-')
    drawPoint(plane[0], color='red')
    drawPoint(plane[1], color='red')

    #projection of the plane on the screen
    P = createProjectionMatrix2x2()
    # project the point and normalize by y
    p0 = P @ plane[0]
    p0[0] = p0[0] / (1+p0[1])
    p1 = P @ plane[1]
    p1[0] = p1[0] / (1+p1[1])
    drawLine([p0[0],0], [p1[0],0], color='darkred', linestyle='-', linewidth=2)

    # draw edges of the projection
    drawLine([p0[0],0], [0,-focal_length], color='darkred', linestyle='--', linewidth=1)
    drawLine([p1[0],0], [0,-focal_length], color='darkred', linestyle='--', linewidth=1)

    # mouse
#    drawLine([0,-focal_length], [x,y])
#    drawPoint([x,y])
    # mouse projection on the screen
    drawPoint([x,0])

    fig.canvas.draw_idle()         # Redraw efficiently


# Event handler for mouse movement
def on_mouse_move(event):
    global mouse
    if event.inaxes == ax:  # Only update if inside the plot
        mouse = [event.xdata, event.ydata]
        drawCurrent()

def on_key(event):
    global planeRotation
    if event.key == 'e':
        if planeRotation > -30:
            planeRotation -= 1
    elif event.key == 'q':
        if planeRotation < 30:
            planeRotation += 1
    drawCurrent()

# Connect the event
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
fig.canvas.mpl_connect('key_press_event', on_key)

# initial draw
mouse = [0,0]
drawCurrent()
plt.show()
