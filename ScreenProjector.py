import numpy as np
import matplotlib.pyplot as plt


# global setup
FOV = 90  # degrees
ScreenWidth = 2
HowScale = 3  # how much wider the screen is shown compared to the actual screen width
PlaneWidth = 1.4  # width of the plane at distance = 1
WindowSizeInInches = 10  # window size in 
RotationStrength = 4.5  # how strong the plane rotation is affected by mouse x position

# derived saetup
HalfScreenWidth = ScreenWidth / 2
HalfPlaneWidth = PlaneWidth / 2

planeRotation = 0  # degrees

# drawing

def drawLine(p1, p2, color='green', linestyle='--', linewidth=1):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linestyle=linestyle, linewidth=linewidth)

def drawPoint(p, color='green', markersize=5, markeredgewidth=2):
    ax.plot(p[0], p[1], marker='o', markersize=markersize, markerfacecolor='none', markeredgecolor=color, markeredgewidth=markeredgewidth)


# math

def createRotationMatrix(angle):
    rad = np.deg2rad(angle)
    c = np.cos(rad)
    s = np.sin(rad)
    return np.array([[c, -s], [s, c]])

def rotatePoint(point, R):
    return R @ point


def createProjectionMatrix2x2(focal_length):
    return np.array([[focal_length, 0], [0, 1]])

def ray_segment_intersection(ray_dir, seg_start, seg_end, eps=1e-9):
    p = np.array([0,0], dtype=float)
    r = np.array(ray_dir, dtype=float)
    q = np.array(seg_start, dtype=float)
    s = np.array(seg_end, dtype=float) - q

    rxs = r[0]*s[1] - r[1]*s[0]
    if abs(rxs) < eps:
        return None  # Parallel or collinear

    q_p = q - p
    t = (q_p[0]*s[1] - q_p[1]*s[0]) / rxs
    u = (q_p[0]*r[1] - q_p[1]*r[0]) / rxs

    if t >= 0 and 0 <= u <= 1:
        intersection = p + t * r
        return intersection
    return None

def angle_between_vectors(v1, v2):
    angle_rad = np.arctan2(v1[0]*v2[1] - v1[1]*v2[0], v1[0]*v2[0] + v1[1]*v2[1])
    angle_deg = np.degrees(angle_rad)
    return angle_deg


# Create a figure and axis
# Remove 'q' from the quit keymap
plt.rcParams['keymap.quit'] = []  # or set to a different key, e.g., ['ctrl+q']
plt.rcParams['keymap.fullscreen'] = []  # or set to a different key, e.g., ['ctrl+q']
fig = plt.figure(figsize=(WindowSizeInInches, WindowSizeInInches/HowScale), dpi=200)  # 10×6 inches at 100 DPI → 1000×600 pixels
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)

# Initial line from (0,0) to (0,0)
#line = ax.plot([0, 0], [0, 0], color='red')

mouse = [0,0]

def drawCurrent():
    focal_length = ScreenWidth / (2 * np.tan(np.deg2rad(FOV) / 2))

#limit the mouse position between -1 and 1
    x = np.clip(mouse[0], -1, +1)
    y = mouse[1]

    #control plane rotation with mouse x position
    global planeRotation
    planeRotation = angle_between_vectors([0,1], [x,RotationStrength])  # angle between the two vectors

    ax.clear()
    ax.set_xlim(-HalfScreenWidth*HowScale, HalfScreenWidth*HowScale)
    ax.set_ylim(-focal_length, HalfPlaneWidth+focal_length)
    plt.grid(True)
    plt.title("FOV={:.0f}, focal length = {:.2f}".format(FOV, focal_length))
    # screen
    drawLine([-HalfScreenWidth,0], [HalfScreenWidth,0], color='blue', linestyle='-')
    #plane
    planeOrig = [[-PlaneWidth/2, 0], [PlaneWidth/2, 0]] ## coordinates of the plane in local plane space
    R = createRotationMatrix(planeRotation)
    plane = [rotatePoint(planeOrig[0], R), rotatePoint(planeOrig[1], R)]  # rotated plane coordinates
    drawLine(plane[0], plane[1], color='red', linestyle='-')
    drawPoint(plane[0], color='red', markersize=2)
    drawPoint(plane[1], color='red', markersize=2)

    #projection of the plane on the screen
    P = createProjectionMatrix2x2(focal_length)
    # project the point and normalize by y
    p0 = P @ [plane[0][0], plane[0][1]+focal_length]
    p0[0] = p0[0] / (p0[1])
    p1 = P @ [plane[1][0], plane[1][1]+focal_length]
    p1[0] = p1[0] / (p1[1])
    drawLine([p0[0],0], [p1[0],0], color='darkred', linestyle='-', linewidth=2)

    # draw edges of the projection
    drawLine([p0[0],0], [0,-focal_length], color='darkred', linestyle='--', linewidth=1)
    drawLine([p1[0],0], [0,-focal_length], color='darkred', linestyle='--', linewidth=1)

    #ray to the mouse
    rayMouse = [x,focal_length]
    drawLine([0,-focal_length], [rayMouse[0],rayMouse[1]-focal_length], color='green', linestyle='--', linewidth=1)

    #intersection
    intersection = ray_segment_intersection(rayMouse, [plane[0][0], plane[0][1] + focal_length], [plane[1][0], plane[1][1]+ focal_length])
    if intersection is not None:
        planeIntersection = [intersection[0], intersection[1]-focal_length]
        drawPoint(planeIntersection, markersize=5, markeredgewidth=1)

        #mouse in plane space
        Rinv = np.linalg.inv(R)
        mouseInPlaneSpace = Rinv @ planeIntersection
        mouseInPlaneSpace[1] = -mouseInPlaneSpace[1]

        #convert mouse position in plane back to view space
        mouseInPlaneSpaceInViewSpace = R @ mouseInPlaneSpace
        drawPoint(mouseInPlaneSpaceInViewSpace, color='red', markersize=3, markeredgewidth=3)
        ax.text(mouseInPlaneSpaceInViewSpace[0], mouseInPlaneSpaceInViewSpace[1], "  {:.2f}".format(mouseInPlaneSpace[0]/HalfPlaneWidth), color='black', fontsize=8, verticalalignment='bottom')
 

    #mouse in view space
    Pinv = np.linalg.inv(P)
    mouseViewSpace = Pinv @ np.array([x,0])
#    mouseViewSpace[0] = mouseViewSpace[0] / (1+mouseViewSpace[1])
    Rinv = np.linalg.inv(R)
    mouseInPlaneSpace = Rinv @ mouseViewSpace
    mouseInPlaneSpace[1] = -mouseInPlaneSpace[1]  # flip y to match the drawing coordinates
#    drawPoint(mouseInPlaneSpace, markersize=5)


    # mouse
#    drawLine([0,-focal_length], [x,y])
#    drawPoint([x,y])
    # mouse projection on the screen
    drawPoint([rayMouse[0],rayMouse[1]-focal_length], markersize=3, markeredgewidth=1)

    fig.canvas.draw_idle()         # Redraw efficiently


# Event handler for mouse movement
def on_mouse_move(event):
    global mouse
    if event.inaxes == ax:  # Only update if inside the plot
        mouse = [event.xdata, event.ydata]
        drawCurrent()

def on_key(event):
    global planeRotation, FOV
    if event.key == 'e':
        if planeRotation > -30:
            planeRotation -= 1
    elif event.key == 'q':
        if planeRotation < 30:
            planeRotation += 1
    elif event.key == 'f':
        if FOV > 50:
            FOV -= 1
    elif event.key == 'F':
        if FOV <130:
            FOV += 1
    drawCurrent()

# Connect the event
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
fig.canvas.mpl_connect('key_press_event', on_key)

# initial draw
mouse = [0,0]
drawCurrent()
plt.show()
