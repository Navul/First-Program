from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window size
W_Width, W_Height = 800, 600

# Camera variables
camera_x, camera_y, camera_z = 0, -400, 200
look_x, look_y, look_z = 0, 0, 0

# Player movement variables
player_speed = 2.0
world_offset = 0.0  # How far the world has moved backward
player_x = 0.0  # Player's left-right position on the road
player_z = 50.0  # Player's vertical position (for jumping)
player_velocity_z = 0.0  # Player's vertical velocity
is_jumping = False
ground_level = 50.0  # Ground level for the player
jump_strength = 15.0  # How strong the jump is
gravity = -0.8  # Gravity pulling player down

# Obstacles
obstacles = []  # List to store obstacles
obstacle_spawn_timer = 0
obstacle_spawn_interval = 90  # Spawn obstacle every 90 frames (slower spawning)

def drawPlayer():
    """
    Draw a 3D player with sphere head, box body, and box arms/legs
    Player position now uses player_x for left-right movement and player_z for jumping
    """
    glPushMatrix()
    glTranslatef(player_x, -250, player_z)  # Use player_z for vertical position (jumping)
    
    # Draw body (main torso)
    glPushMatrix()
    glColor3f(0.0, 0.3, 0.0)  # Dark green for body
    glTranslatef(0, 0, 30)  # Raise body up
    glScalef(20, 15, 40)  # Scale to make body shape
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw head (sphere)
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.4)  # Skin color
    glTranslatef(0, 0, 60)  # Position above body
    glutSolidSphere(12, 20, 20)  # radius, slices, stacks
    glPopMatrix()
    
    # Draw left arm
    glPushMatrix()
    glColor3f(0.0, 0.3, 0.0)  # Same color as body
    glTranslatef(-15, 0, 25)  # Position to left side
    glScalef(8, 8, 25)  # Scale to arm shape
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw right arm
    glPushMatrix()
    glColor3f(0.0, 0.3, 0.0)  # Same color as body
    glTranslatef(15, 0, 25)  # Position to right side
    glScalef(8, 8, 25)  # Scale to arm shape
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw left leg
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.5)  # Blue for legs
    glTranslatef(-8, 0, -5)  # Position below body
    glScalef(8, 8, 30)  # Scale to leg shape
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw right leg
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.5)  # Blue for legs
    glTranslatef(8, 0, -5)  # Position below body
    glScalef(8, 8, 30)  # Scale to leg shape
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def keyboardListener(key, x, y):
    """
    Handle keyboard input for camera movement
    W/S - Move camera forward/backward
    A/D - Move camera left/right
    Q/E - Move camera up/down
    Space - Jump
    """
    global camera_x, camera_y, camera_z, player_x, is_jumping, player_velocity_z
    
    if key == b'w':  # Move camera forward
        camera_y += 20
        print("Camera moved forward")
    elif key == b's':  # Move camera backward
        camera_y -= 20
        print("Camera moved backward")
    elif key == b'a':  # Move camera left
        camera_x -= 20
        print("Camera moved left")
    elif key == b'd':  # Move camera right
        camera_x += 20
        print("Camera moved right")
    elif key == b'q':  # Move camera up
        camera_z += 20
        print("Camera moved up")
    elif key == b'e':  # Move camera down
        camera_z -= 20
        print("Camera moved down")
    elif key == b'r':  # Reset camera
        camera_x, camera_y, camera_z = 0, -400, 200
        player_x = 0.0  # Also reset player position
        print("Camera and player reset")
    elif key == b' ':  # Space key for jumping
        if not is_jumping:  # Can only jump if not already jumping
            is_jumping = True
            player_velocity_z = jump_strength
            print("Player jumped!")
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    """
    Handle special keys (arrow keys) for player left/right movement
    """
    global player_x
    
    if key == GLUT_KEY_LEFT:  # Move player left
        player_x -= 15
        # Keep player within road bounds (approximate road width)
        if player_x < -200:
            player_x = -200
        print("Player moved left")
    elif key == GLUT_KEY_RIGHT:  # Move player right
        player_x += 15
        # Keep player within road bounds (approximate road width)
        if player_x > 200:
            player_x = 200
        print("Player moved right")
    
    glutPostRedisplay()

def animate():
    """
    Animation function to move the world forward (player moving backward effect)
    Also handles player jumping physics and obstacle management
    """
    global world_offset, player_z, player_velocity_z, is_jumping
    
    # Move world forward
    world_offset -= player_speed  # Move world forward to simulate backward movement
    
    # Handle jumping physics
    if is_jumping:
        # Update player vertical position
        player_z += player_velocity_z
        # Apply gravity to velocity
        player_velocity_z += gravity
        
        # Check if player has landed
        if player_z <= ground_level:
            player_z = ground_level  # Set to ground level
            player_velocity_z = 0.0  # Stop vertical movement
            is_jumping = False  # Player is no longer jumping
    
    # Handle obstacles
    spawnObstacles()
    updateObstacles()
    checkCollisions()
    
    glutPostRedisplay()

def drawBackground():
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Night sky color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def drawRoad():
    """
    Draw infinite road as one continuous strip using GL_TRIANGLE_STRIP
    """
    glColor3f(0.3, 0.3, 0.3)  # Road color
    
    # Create road points that extend well beyond visible area
    road_segments = 20  # Number of road segments
    segment_length = 100  # Length of each segment
    
    # Start road well before visible area and extend well beyond
    start_y = -1000 + (world_offset % segment_length)
    
    glBegin(GL_TRIANGLE_STRIP)
    
    for i in range(road_segments + 1):
        y = start_y + i * segment_length
        
        # Calculate road width at this point (perspective effect)
        # Far distance = narrow, close distance = wide
        progress = (y + 1000) / 2000.0  # 0 to 1 progression
        left_x = -250 + progress * 150   # Goes from -250 to -100
        right_x = 250 - progress * 150   # Goes from 250 to 100
        
        # Add two vertices for this cross-section of road
        glVertex2f(left_x, y)   # Left edge
        glVertex2f(right_x, y)  # Right edge
    
    glEnd()

def drawRoadMarkings():
    """
    Draw white dashed lines in the middle of the road for animation visibility
    """
    glColor3f(1.0, 1.0, 1.0)  # White color for road markings
    
    # Draw dashed white lines in the center
    marking_length = 40
    marking_gap = 60
    total_segment = marking_length + marking_gap
    
    # Start markings well before visible area
    start_y = -1000 + (world_offset % total_segment)
    
    # Draw multiple marking segments
    for i in range(25):  # Draw many segments to cover entire road
        y_start = start_y + i * total_segment
        y_end = y_start + marking_length
        
        # Calculate road center width at this point (perspective effect)
        progress_start = (y_start + 1000) / 2000.0
        progress_end = (y_end + 1000) / 2000.0
        
        center_width = 3  # Width of the marking line
        
        glBegin(GL_QUADS)
        glVertex2f(-center_width, y_start)  # Bottom left
        glVertex2f(center_width, y_start)   # Bottom right
        glVertex2f(center_width, y_end)     # Top right
        glVertex2f(-center_width, y_end)    # Top left
        glEnd()

def createObstacle(obstacle_type, x_position):
    """
    Create different types of obstacles
    obstacle_type: 'low' (jump over) or 'tall' (move left/right)
    x_position: x position on the road (-150 to 150)
    """
    obstacle = {
        'type': obstacle_type,
        'x': x_position,
        'y': 600,  # Start closer to player for visibility
        'active': True
    }
    return obstacle

def drawObstacles():
    """
    Draw all active obstacles
    """
    for obstacle in obstacles:
        if not obstacle['active']:
            continue
            
        glPushMatrix()
        glTranslatef(obstacle['x'], obstacle['y'] + world_offset, 0)
        
        if obstacle['type'] == 'low':
            # Low obstacle - jump over (red color)
            glColor3f(1.0, 0.0, 0.0)  # Red
            glTranslatef(0, 0, 25)  # Raise slightly above ground
            glScalef(40, 60, 30)  # Wide, long, low
            glutSolidCube(1)
        elif obstacle['type'] == 'tall':
            # Tall obstacle - move left/right (blue color)
            glColor3f(0.0, 0.0, 1.0)  # Blue
            glTranslatef(0, 0, 80)  # Raise high above ground
            glScalef(40, 60, 120)  # Wide, long, tall
            glutSolidCube(1)
            
        glPopMatrix()

def spawnObstacles():
    """
    Spawn new obstacles periodically at random positions across the road
    """
    global obstacle_spawn_timer
    import random
    
    obstacle_spawn_timer += 1
    
    if obstacle_spawn_timer >= obstacle_spawn_interval:
        obstacle_spawn_timer = 0
        
        # Randomly choose obstacle type
        obstacle_type = random.choice(['low', 'tall'])
        
        # Random x position across the full width of the road
        # Road width goes from approximately -200 to +200 at player level
        x_position = random.randint(-180, 180)  # Random position across road width
        
        # Create and add obstacle
        new_obstacle = createObstacle(obstacle_type, x_position)
        obstacles.append(new_obstacle)
        print(f"Spawned {obstacle_type} obstacle at x={x_position}. Total obstacles: {len(obstacles)}")

def updateObstacles():
    """
    Update obstacle positions and remove old ones
    """
    global obstacles
    obstacles_to_remove = []
    
    for obstacle in obstacles:
        # Mark obstacles for removal if they have passed the player
        # Player is at y = -250, so remove obstacles that are well behind
        if obstacle['y'] + world_offset < -400:  # Remove when well past player
            obstacles_to_remove.append(obstacle)
    
    # Remove old obstacles
    for obstacle in obstacles_to_remove:
        obstacles.remove(obstacle)
        if len(obstacles_to_remove) > 0:  # Only print when actually removing
            print(f"Removed obstacle. Remaining obstacles: {len(obstacles)}")

def checkCollisions():
    """
    Check if player collides with any obstacles
    """
    player_size = 30  # Approximate player size
    
    for obstacle in obstacles:
        if not obstacle['active']:
            continue
            
        # Calculate obstacle position relative to world
        obs_x = obstacle['x']
        obs_y = obstacle['y'] + world_offset
        
        # Check if obstacle is near player's y position
        if abs(obs_y - (-250)) < 50:  # Player is at y = -250
            # Check x collision
            if abs(player_x - obs_x) < 50:  # Close in x direction
                if obstacle['type'] == 'low':
                    # Low obstacle - check if player is jumping high enough
                    if player_z < 80:  # Not jumping high enough
                        print("Hit low obstacle! Should have jumped!")
                        obstacle['active'] = False
                elif obstacle['type'] == 'tall':
                    # Tall obstacle - check if player is on ground (not jumping away)
                    if player_z <= ground_level + 10:  # On or near ground
                        print("Hit tall obstacle! Should have moved left/right!")
                        obstacle['active'] = False

def drawBuilding(base_left, base_right, top_left, top_right, rows=6, color=(0.5, 0.7, 0.9), window_color=(0.85, 0.92, 1.0)):
    """
    Draws a trapezoidal building with perspective, base wider than top.
    Now adjusts position based on world_offset for infinite movement effect
    """
    # Adjust building position based on world movement
    adj_base_left = (base_left[0], base_left[1] + world_offset)
    adj_base_right = (base_right[0], base_right[1] + world_offset)
    adj_top_left = (top_left[0], top_left[1] + world_offset)
    adj_top_right = (top_right[0], top_right[1] + world_offset)
    
    # Only draw if building is in visible range
    if adj_base_left[1] < -600 or adj_base_left[1] > 600:
        return
    
    # Draw building body
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(*adj_base_left)
    glVertex2f(*adj_base_right)
    glVertex2f(*adj_top_right)
    glVertex2f(*adj_top_left)
    glEnd()

    # Draw windows in perspective
    glColor3f(*window_color)
    for r in range(rows):
        # Calculate y positions for this row
        y_ratio = (r + 0.1) / rows
        y_ratio_next = (r + 0.9) / rows
        y0 = adj_base_left[1] + (adj_top_left[1] - adj_base_left[1]) * y_ratio
        y1 = adj_base_left[1] + (adj_top_left[1] - adj_base_left[1]) * y_ratio_next
        
        # Calculate x positions for this row (perspective)
        left_x = adj_base_left[0] + (adj_top_left[0] - adj_base_left[0]) * y_ratio
        right_x = adj_base_right[0] + (adj_top_right[0] - adj_base_right[0]) * y_ratio
        
        # Draw 3 windows per row
        for w in range(3):
            window_width = (right_x - left_x) / 5  # Divide into 5 parts for spacing
            wx0 = left_x + window_width * (0.5 + w * 1.5)
            wx1 = wx0 + window_width * 0.7
            
            glBegin(GL_QUADS)
            glVertex2f(wx0, y0)
            glVertex2f(wx1, y0)
            glVertex2f(wx1, y1)
            glVertex2f(wx0, y1)
            glEnd()

def drawBuildings():
    """
    Draw multiple buildings at different positions for infinite effect
    """
    # Building templates with different sizes and colors
    buildings = [
        # Left side buildings
        ((-280, -300), (-220, -300), (-270, 200), (-230, 200), 8, (0.5, 0.7, 0.9)),
        ((-280, 300), (-220, 300), (-270, 800), (-230, 800), 6, (0.7, 0.5, 0.8)),
        ((-280, 900), (-220, 900), (-270, 1400), (-230, 1400), 10, (0.6, 0.8, 0.5)),
        # Right side buildings  
        ((220, -300), (280, -300), (230, 200), (270, 200), 7, (0.8, 0.6, 0.4)),
        ((220, 300), (280, 300), (230, 800), (270, 800), 9, (0.4, 0.6, 0.8)),
        ((220, 900), (280, 900), (230, 1400), (270, 1400), 5, (0.9, 0.7, 0.5)),
    ]
    
    # Draw buildings at multiple offsets to create infinite effect
    for offset in range(-2, 3):  # Draw buildings at different y offsets
        for base_left, base_right, top_left, top_right, rows, color in buildings:
            # Offset each building set
            offset_y = offset * 1200
            adj_base_left = (base_left[0], base_left[1] + offset_y)
            adj_base_right = (base_right[0], base_right[1] + offset_y)
            adj_top_left = (top_left[0], top_left[1] + offset_y)
            adj_top_right = (top_right[0], top_right[1] + offset_y)
            
            drawBuilding(adj_base_left, adj_base_right, adj_top_left, adj_top_right, 
                        rows, color, (0.9, 0.9, 0.9))

def display():
    drawBackground()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Set up 3D perspective view
    gluLookAt(camera_x, camera_y, camera_z,    # Camera position
              look_x, look_y, look_z,          # Look at center
              0, 0, 1)                         # Up vector
    
    # Enable depth testing for 3D
    glEnable(GL_DEPTH_TEST)
    
    # Draw road
    drawRoad()
    # Draw road markings for animation visibility
    drawRoadMarkings()
    # Draw multiple buildings for infinite effect
    drawBuildings()
    
    # Draw obstacles
    drawObstacles()
    
    # Draw 3D player in middle of road (player stays at center)
    drawPlayer()
    
    glutSwapBuffers()

def init():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, W_Width/W_Height, 0.1, 1000)  # 3D perspective projection

def main():
    glutInit()
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Added depth buffer
    glutCreateWindow(b"OpenGL City Draft")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(animate)  # Changed from display to animate
    glutMainLoop()

if __name__ == "__main__":
    main()
