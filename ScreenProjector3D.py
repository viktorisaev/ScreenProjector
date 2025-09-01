import numpy as np
import matplotlib.pyplot as plt


# global setup
FOV = 90  # degrees
ScreenWidth = 2
HowScale = 1  # how much wider the screen is shown compared to the actual screen width
Plane = [1.6, 0.9]  # width of the plane at distance = 1
WindowSizeInInches = 10  # window size in 
RotationStrength = 3.3  # how strong the plane rotation is affected by mouse x position

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



#math

def rotation_matrix_from_vectors(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    axis = np.cross(a, b)
    s = np.linalg.norm(axis)
    angle = np.arccos(np.clip(np.dot(a, b), -1.0, 1.0))
    if s == 0:
        # Parallel vectors: either identity or 180° rotation
        return np.eye(3) if angle > 0 else -np.eye(3)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R

def create_projection_matrix(focal_length):
    #define a projection matrix in 3D
    P = np.array([[focal_length,    0,              0],
                  [0,               focal_length,   0],
                  [0,               0,              1]])
    return P

def project_points(points, P):
    projected = []
    for p in points:
        p_projected = P @ p
        p_projected /= p_projected[2]  # Normalize by the third coordinate
        projected.append(p_projected[:2])
    return projected


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

    # rotate
    planeOrig = [[-HalfPlane[0], -HalfPlane[1], focal_length], [-HalfPlane[0], HalfPlane[1], focal_length], [HalfPlane[0], -HalfPlane[1], focal_length], [HalfPlane[0], HalfPlane[1], focal_length]] ## coordinates of the plane in local plane space
    mouseRay = np.array([-x, -y, RotationStrength])
    planeNormal = [0,0,1]
    R = rotation_matrix_from_vectors(mouseRay, planeNormal)
    planeRotated = [R @ np.array(planeOrig[0]), R @ np.array(planeOrig[1]), R @ np.array(planeOrig[2]), R @ np.array(planeOrig[3])]  # rotated plane coordinates

    # projection
    P = create_projection_matrix(focal_length)
    planeRotatedProjected = project_points(planeRotated, P)

    #draw the quadrangle
    drawQuadrangle(planeRotatedProjected)

    #mouse position in the quadrangle
    mousePlaneX = np.clip(x, -HalfPlane[0], HalfPlane[0])
    mousePlaneY = np.clip(y, -HalfPlane[1], HalfPlane[1]) # limit mouse position to be inside the plane
    horMouse = [[-HalfPlane[0], mousePlaneY, focal_length], [HalfPlane[0], mousePlaneY, focal_length]]
    vertMouse = [[mousePlaneX, -HalfPlane[1], focal_length], [mousePlaneX, HalfPlane[1], focal_length]]
    #draw mouse cross
    horMouseRotated = [R @ np.array(horMouse[0]), R @ np.array(horMouse[1])]
    vertMouseRotated = [R @ np.array(vertMouse[0]), R @ np.array(vertMouse[1])]
    horMouseProjected = project_points(horMouseRotated, P)
    vertMouseProjected = project_points(vertMouseRotated, P)
    drawLine(horMouseProjected[0], horMouseProjected[1], color='green', linestyle='-', linewidth=1)
    drawLine(vertMouseProjected[0], vertMouseProjected[1], color='green', linestyle='-', linewidth=1)

    # draw mouse position in screen space. SHould later match the position in the plane space
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
fig = plt.figure(figsize=(WindowSizeInInches, WindowSizeInInches/HowScale), dpi=120)  # 10×6 inches at 100 DPI → 1000×600 pixels
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)

# Connect the event
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
fig.canvas.mpl_connect('key_press_event', on_key)

# initial draw
drawCurrent()
plt.show()
