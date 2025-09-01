import numpy as np
import matplotlib.pyplot as plt


# global setup
FOV = 90  # degrees
ScreenWidth = 2
HowScale = 1  # how much wider the screen is shown compared to the actual screen width
Plane = [1.6, 0.9]  # width of the plane at distance = 1
WindowSizeInInches = 10  # window size in 
RotationStrength = 4.5  # how strong the plane rotation is affected by mouse x position

# derived saetup
HalfScreen = [ScreenWidth / 2, ScreenWidth / 2]
HalfPlane = [x/2 for x in Plane]


# drawing
def drawLine(p1, p2, color='green', linestyle='--', linewidth=1):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linestyle=linestyle, linewidth=linewidth)

def drawPoint(p, color='green', markersize=5, markeredgewidth=2):
    ax.plot(p[0], p[1], marker='o', markersize=markersize, markerfacecolor='none', markeredgecolor=color, markeredgewidth=markeredgewidth)



def drawQuadrangle(pp):
    color = 'red'
    linewidth = 2
    linestyle = '-'
    drawLine(pp[0], pp[1], color=color, linewidth=linewidth, linestyle=linestyle)
    drawLine(pp[0], pp[2], color=color, linewidth=linewidth, linestyle=linestyle)
    drawLine(pp[1], pp[3], color=color, linewidth=linewidth, linestyle=linestyle)
    drawLine(pp[2], pp[3], color=color, linewidth=linewidth, linestyle=linestyle)

def drawCurrent():
    focal_length = ScreenWidth / (2 * np.tan(np.deg2rad(FOV) / 2))

#limit the mouse position between -1 and 1
    x = np.clip(mouse[0], -1, +1)
    y = mouse[1]

    ax.clear()
    ax.set_xlim(-HalfScreen[0]*HowScale, HalfScreen[0]*HowScale)
    ax.set_ylim(-HalfScreen[1], HalfScreen[1])
    plt.grid(True)
#    plt.title("FOV={:.0f}, focal length = {:.2f}".format(FOV, focal_length))

    planeOrig = [[-HalfPlane[0], -HalfPlane[1]], [-HalfPlane[0], HalfPlane[1]], [HalfPlane[0], -HalfPlane[1]], [HalfPlane[0], HalfPlane[1]]] ## coordinates of the plane in local plane space

    drawQuadrangle(planeOrig)

    drawPoint([x,y], markersize=3)

    fig.canvas.draw_idle()         # Redraw efficiently

# Event handler for mouse movement
def on_mouse_move(event):
    global mouse
    if event.inaxes == ax:  # Only update if inside the plot
        mouse = [event.xdata, event.ydata]
        drawCurrent()

def on_key(event):
    if event.key == 'f':
        if FOV > 50:
            FOV -= 1
    elif event.key == 'F':
        if FOV <130:
            FOV += 1
    drawCurrent()

# global setup
mouse = [0,0]

# Create a figure and axis
plt.rcParams['keymap.quit'] = []  # or set to a different key, e.g., ['ctrl+q']
plt.rcParams['keymap.fullscreen'] = []  # or set to a different key, e.g., ['ctrl+q']
fig = plt.figure(figsize=(WindowSizeInInches, WindowSizeInInches/HowScale), dpi=100)  # 10×6 inches at 100 DPI → 1000×600 pixels
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)

# Connect the event
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
fig.canvas.mpl_connect('key_press_event', on_key)

# initial draw
drawCurrent()
plt.show()
