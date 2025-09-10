from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time  # Add time module for speed progression

# Window size
W_Width, W_Height = 800, 600

# Camera variables
camera_x, camera_y, camera_z = 0, -400, 200
look_x, look_y, look_z = 0, 0, 0

# Border constants
X_MIN, X_MAX = -250, 250
Y_MIN, Y_MAX = -1000, 1000
Z_MIN, Z_MAX = 0, 200

# Player movement variables
player_speed = 2.0
initial_speed = 2.0  # Store initial speed for reference
max_speed = 8.0  # Maximum speed limit
speed_increase_interval = 10.0  # Increase speed every 10 seconds
speed_increase_amount = 0.5  # How much to increase speed each time
game_start_time = 0.0  # Track when game started
last_speed_increase_time = 0.0  # Track last speed increase
world_offset = 0.0  # How far the world has moved backward
player_x = 0.0  # Player's left-right position on the road
player_z = 50.0  # Player's vertical position (for jumping)
player_velocity_z = 0.0  # Player's vertical velocity
is_jumping = False
ground_level = 50.0  # Ground level for the player
jump_strength = 15.0  # How strong the jump is
gravity = -0.5  # Gravity pulling player down

# Game state variables
game_over = False
game_won = False
score = 0
game_paused = False
super_power_active = False
silver_power_count = 0  # Number of silver power-ups player has (max 3)
max_silver_power = 3  # Maximum silver power-ups player can have
bullets = []
move_speed = 2.0
player_lives = 3  # Player starts with 3 lives
bullet_ammo = 0  # Player starts with 0 bullets
max_ammo = 5  # Maximum bullets player can carry
player_stunned = False  # Player is stunned by tall obstacle, can't move but game continues
low_obstacle_hits = 0  # Track how many times player hit low obstacles
shot_speed = 10  # Bullet movement speed
player_pos = [0, 20, 0]

# Ghost variables for chasing behavior
ghost_x = 30.0  # Ghost's independent x position
ghost_chase_speed = 1.0  # How fast ghost chases player
ghost_y_offset = -80  # Ghost's y position offset from player (starts close)
ghost_hide_timer = 0.0  # Timer to track when to hide ghost
ghost_hidden = False  # Whether ghost has moved to hidden position
ghost_retreat_speed = 5.0  # How fast ghost moves back (units per frame)
ghost_target_y_offset = -80  # Target y position for ghost
ghost_awakened = False  # Whether ghost has been permanently awakened by low obstacle hit

# Cheat mode variables
cheat_mode = False  # Cheat mode toggle

# UFO variables
ufo_x = 0.0  # UFO's x position
ufo_y = 100.0  # UFO's y position (above player)
ufo_z = 150.0  # UFO's height (in the sky)
ufo_active = False  # Whether UFO is currently active
ufo_spawn_timer = 0  # Timer for UFO spawning
ufo_spawn_interval = 600  # UFO appears every 10 seconds (600 frames at 60fps)
ufo_bullets = []  # List of UFO bullets
ufo_bullet_timer = 0  # Timer for UFO shooting
ufo_bullet_interval = 120  # UFO shoots every 2 seconds when active

# Obstacles - Three types
power_ups = []  # Power-ups that give benefits when collected
ground_obstacles = []  # Low obstacles that must be jumped over
full_obstacles = []  # Tall obstacles that must be avoided by moving left/right
obstacles = []  # Original obstacle system for compatibility
obstacle_spawn_timer = 0
obstacle_spawn_interval = 90  # Spawn obstacle every 90 frames
class CBullet:
    def __init__(self, x, y, z):
        self.loc = [x, y + 20, z]  # Start slightly ahead of player
        self.dir = [0, 1, 0]  # Move forward along Y-axis (road direction)
        self.active = True
         
    def update_position(self):
        if self.active:
            self.loc[0] += self.dir[0] * shot_speed
            self.loc[1] += self.dir[1] * shot_speed  # Move forward along road
            self.loc[2] += self.dir[2] * shot_speed
            
            # Deactivate bullets that go too far ahead
            if self.loc[1] > 200:  # Remove when bullets get ahead of visible area
                self.active = False

class CUFOBullet:
    def __init__(self, x, y, z):
        self.loc = [x, y, z]  # Start at UFO position [x, height, forward]
        self.dir = [0, -1, 0]  # Move downward (negative Y direction = downward)
        self.active = True
         
    def update_position(self):
        if self.active:
            # UFO bullets move downward toward ground
            self.loc[1] += self.dir[1] * 3  # Move down at speed 3
            
            # Deactivate bullets that hit the ground
            if self.loc[1] < 0:  # Remove when bullets hit ground level
                self.active = False

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
    gluSphere(gluNewQuadric(), 12, 20, 20)  # radius, slices, stacks
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

def drawUFO():
    """
    Draw a simple UFO using only allowed OpenGL functions
    UFO consists of a main disc and a dome on top
    """
    if not ufo_active:
        return
        
    glPushMatrix()
    glTranslatef(ufo_x, ufo_z + world_offset, 25.0)  # Position UFO higher in the sky
    
    # UFO main disc (flattened cube)
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)  # Metallic gray color
    glScalef(6, 6, 1)  # Wide and flat like a disc
    glutSolidCube(1)
    glPopMatrix()
    
    # UFO dome (smaller cube on top)
    glPushMatrix()
    glColor3f(0.5, 0.8, 1.0)  # Light blue dome
    glTranslatef(0, 0, 1.5)  # Position above the disc
    glScalef(3, 3, 2)  # Smaller dome shape
    glutSolidCube(1)
    glPopMatrix()
    
    # UFO lights (small cubes around the disc)
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90, 0, 0, 1)  # Rotate around Z-axis for each light
        glTranslatef(4, 0, 0)  # Position light on edge of disc
        glColor3f(1.0, 1.0, 0.0)  # Yellow light
        glScalef(0.5, 0.5, 0.5)  # Small light
        glutSolidCube(1)
        glPopMatrix()
    
    glPopMatrix()

def drawUFOBullet(bullet):
    """
    Draw UFO bullet using only allowed OpenGL functions
    """
    if not bullet.active:
        return
        
    glPushMatrix()
    glTranslatef(bullet.loc[0], bullet.loc[1] + world_offset, bullet.loc[2])
    glColor3f(1.0, 0.0, 0.0)  # Red UFO bullet
    glScalef(5, 5, 10)  # Elongated bullet shape
    glutSolidCube(1)
    glPopMatrix()

def drawGhost():
    """
    Draw a ghost behind the main player using only allowed OpenGL functions.
    Ghost is positioned behind the player to appear as if chasing.
    """
    glPushMatrix()
    # Position ghost behind player using independent ghost_x position
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Use dynamic ghost_y_offset
    
    # Ghost body (semi-transparent white/light blue)
    glColor3f(0.8, 0.9, 1.0)  # Light blue-white color
    glTranslatef(0, 0, 30)  # Raise body up
    glScalef(18, 12, 35)  # Scale to make ghost body shape
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Same base position using dynamic offset
    
    # Ghost head (white sphere)
    glColor3f(0.1, 0.1, 0.1)  # Black for head
    glTranslatef(0, 0, 55)  # Position above body
    gluSphere(gluNewQuadric(), 10, 15, 15)  # Slightly smaller than player head
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Same base position using dynamic offset
    
    # Left devil horn (dark red)
    glColor3f(0.6, 0.1, 0.1)  # Dark red color for horn
    glTranslatef(-6, 0, 59)   # Position on left side of head, above it
    quad = gluNewQuadric()
    gluCylinder(quad, 3, 0, 17, 12, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Same base position using dynamic offset
    
    # Right devil horn (dark red)
    glColor3f(0.6, 0.1, 0.1)  # Dark red color for horn
    glTranslatef(6, 0, 59)    # Position on right side of head, above it
    quad = gluNewQuadric()
    gluCylinder(quad, 3, 0, 17, 12, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Same base position using dynamic offset
    
    # Ghost left arm (floating)
    glColor3f(0.8, 0.9, 1.0)  # Same color as body
    glTranslatef(-12, 13, 37)  # Position to left side
    glScalef(6, 35, 6)  # Scale to arm shape
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(ghost_x, -250 + ghost_y_offset, player_z)  # Same base position using dynamic offset
    
    # Ghost right arm (floating)
    glColor3f(0.8, 0.9, 1.0)  # Same color as body
    glTranslatef(12, 13, 37)  # Position to right side
    glScalef(6, 35, 6)  # Scale to arm shape
    glutSolidCube(1)
    glPopMatrix()

def keyboardListener(key, x, y):
    """
    Handle keyboard input for camera movement
    W/S - Move camera forward/backward
    A/D - Move camera left/right
    Q/E - Move camera up/down
    Space - Pause/Unpause game
    J - Jump
    """
    global camera_x, camera_y, camera_z, player_x, is_jumping, player_velocity_z, game_paused
    
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
    elif key == b'r':  # Reset camera or restart game
        if game_over or game_won:
            restart_game()
        else:
            camera_x, camera_y, camera_z = 0, -400, 200
            player_x = 0.0  # Also reset player position
            print("Camera and player reset")
    elif key == b' ':  # Space key for pausing/unpausing
        game_paused = not game_paused
        if game_paused:
            print("Game PAUSED - Press SPACE to resume")
        else:
            print("Game RESUMED")
    elif key == b'j':  # J key for jumping
        if not game_paused and not game_over and not game_won:
            if not is_jumping:  # Jump
                is_jumping = True
                player_velocity_z = jump_strength
                print("Player jumped!")
    elif key == b'f':  # F key for shooting bullets (like reference mouse click)
        if not game_paused and not game_over and not game_won:
            shoot_bullet()
    elif key == b'c':  # C key for cheat mode toggle
        global cheat_mode
        cheat_mode = not cheat_mode
        if cheat_mode:
            print("CHEAT MODE ACTIVATED!")
            print("- Unlimited bullets")
            print("- Auto dodge obstacles")
        else:
            print("CHEAT MODE DEACTIVATED!")
    elif key == b'u':  # U key to force update all obstacle positions
        # forceUpdateAllObstaclePositions()
        print("All obstacles forcefully repositioned!")
    elif key == b'i':  # I key to reinitialize obstacles completely
        print("All obstacles reinitialized!")
    elif key == b'r':  # R key to restart game
        restart_game()
    elif key == b'p':  # P key to pause/unpause
        game_paused = not game_paused
        if game_paused:
            print("Game paused")
        else:
            print("Game resumed")
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    """
    Handle special keys (arrow keys) for player left/right movement
    """
    global player_x, player_stunned
    
    # Don't allow movement if player is stunned
    if player_stunned:
        print("Player is stunned and cannot move!")
        return
    
    # Calculate road boundaries at player level (y = -250)
    # Road width calculation based on perspective effect from drawRoad()
    player_y = -250
    progress = (player_y + 1000) / 2000.0  # 0 to 1 progression
    road_left = -250 + progress * 150   # Left boundary at player level
    road_right = 250 - progress * 150   # Right boundary at player level
    
    if key == GLUT_KEY_LEFT:  # Move player left
        player_x -= 15
        # Keep player within road bounds with padding
        padding = 25  # Keep player away from road edges
        if player_x < road_left + padding:
            player_x = road_left + padding
        print("Player moved left")
    elif key == GLUT_KEY_RIGHT:  # Move player right
        player_x += 15
        # Keep player within road bounds with padding
        padding = 25  # Keep player away from road edges
        if player_x > road_right - padding:
            player_x = road_right - padding
        print("Player moved right")
    
    glutPostRedisplay()

<<<<<<< HEAD
def auto_dodge_obstacles():
    """
    Auto-dodge functionality for cheat mode
    Automatically moves player or makes player jump to avoid obstacles
    """
    global player_x, is_jumping, player_velocity_z
    
    # Calculate road boundaries at player level for safe dodging
    player_y = -250
    progress = (player_y + 1000) / 2000.0
    road_left = -250 + progress * 150
    road_right = 250 - progress * 150
    padding = 25
    
    # Look for incoming obstacles that are close to the player
    for obstacle in obstacles:
        if not obstacle['active']:
            continue
            
        obs_x = obstacle['x']
        obs_y = obstacle['y'] + world_offset
        
        # Check if obstacle is approaching (within dodge range)
        if -350 < obs_y < -200:  # Obstacle is approaching player (y = -250)
            # Check if obstacle is in player's path
            if abs(player_x - obs_x) < 40:  # Obstacle is close to player's x position
                
                if obstacle['type'] == 'low':
                    # Auto-jump for low obstacles
                    if not is_jumping and player_z <= ground_level:
                        is_jumping = True
                        player_velocity_z = jump_strength
                        print("Cheat mode: Auto-jumped over low obstacle!")
                        
                elif obstacle['type'] == 'tall':
                    # Auto-dodge left or right for tall obstacles
                    # Choose the side that keeps player within road bounds
                    if player_x > obs_x:
                        # Player is to the right of obstacle, move further right
                        new_x = player_x + 50
                        if new_x <= road_right - padding:
                            player_x = new_x
                            print("Cheat mode: Auto-dodged right!")
                        else:
                            # Can't go right, go left instead
                            new_x = player_x - 50
                            if new_x >= road_left + padding:
                                player_x = new_x
                                print("Cheat mode: Auto-dodged left!")
                    else:
                        # Player is to the left of obstacle, move further left
                        new_x = player_x - 50
                        if new_x >= road_left + padding:
                            player_x = new_x
                            print("Cheat mode: Auto-dodged left!")
                        else:
                            # Can't go left, go right instead
                            new_x = player_x + 50
                            if new_x <= road_right - padding:
                                player_x = new_x
                                print("Cheat mode: Auto-dodged right!")

  
=======
def updateUFO():
    """
    Update UFO behavior: spawning, movement, and shooting
    """
    global ufo_active, ufo_spawn_timer, ufo_x, ufo_z, ufo_bullet_timer, game_over
    
    # UFO spawning logic
    ufo_spawn_timer += 1
    
    if not ufo_active and ufo_spawn_timer >= ufo_spawn_interval:
        # Spawn UFO at random position
        ufo_active = True
        ufo_x = random.uniform(X_MIN + 5, X_MAX - 5)  # Random x position across road
        ufo_z = -100  # Start ahead of player (in front)
        ufo_spawn_timer = 0
        print("UFO appeared in the sky!")
    
    if ufo_active:
        # Move UFO slowly toward player
        ufo_z += 3  # Move toward player
        
        # UFO shooting logic
        ufo_bullet_timer += 1
        if ufo_bullet_timer >= ufo_bullet_interval:
            # UFO shoots at player (bullet starts at UFO position)
            ufo_bullets.append(CUFOBullet(ufo_x, 25.0, ufo_z))  # Start at UFO height
            ufo_bullet_timer = 0
            print("UFO fired a bullet!")
        
        # Remove UFO when it goes too far behind player
        if ufo_z > 200:
            ufo_active = False
            print("UFO disappeared")
    
    # Update UFO bullets
    for bullet in ufo_bullets[:]:  # Use slice to avoid modification during iteration
        if bullet.active:
            bullet.update_position()
            
            # Check collision with player
            dx = bullet.loc[0] - player_x
            dy = bullet.loc[1] - (-250)  # Player is at y = -250
            dz = bullet.loc[2] - player_z
            distance = (dx**2 + dy**2 + dz**2)**0.5
            
            if distance < 30:  # Collision threshold
                if silver_power_count > 0:
                    print(f"UFO bullet hit but PROTECTED by silver power! ({silver_power_count-1} remaining)")
                    score += 15  # Bonus points for surviving UFO attack with silver power
                    silver_power_count -= 1  # Use one silver power
                    bullet.active = False
                else:
                    print("UFO bullet hit player! GAME OVER!")
                    print("================================================")
                    print("                GAME OVER!")
                    print(f"              FINAL SCORE: {score}")
                    print("      Press 'R' to restart the game")
                    print("================================================")
                    game_over = True
                    bullet.active = False
        
        # Remove inactive bullets
        if not bullet.active:
            ufo_bullets.remove(bullet)
>>>>>>> f3e477cf980c6a43f5c9188fbf9ef8a0707a88d4

def animate():
    """
    Animation function to move the world forward (player moving backward effect)
    Also handles player jumping physics and obstacle management
    """
    global world_offset, player_z, player_velocity_z, is_jumping, score, player_stunned
    global game_over, game_won, game_paused  # Add game state variables
    global ghost_x, ghost_hide_timer, ghost_y_offset, ghost_hidden, ghost_retreat_speed, ghost_target_y_offset, ghost_awakened  # Add ghost variables
    
    # Don't update game if paused, game over, or won (but continue if player is just stunned)
    if game_paused or game_over or game_won:
        glutPostRedisplay()
        return
    
    # Update speed progression based on time
    update_speed_progression()
    
    # Move world forward with current speed
    world_offset -= player_speed  # Move world forward to simulate backward movement
    
    # Increase score based on distance traveled
    score += int(player_speed * 0.1)  # Score increases faster with higher speed
    
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
    
    # Handle bullets
    update_bullets()
    
    # Auto-dodge functionality in cheat mode
    if cheat_mode:
        auto_dodge_obstacles()
    
    # Ghost chasing logic - ghost gradually moves toward player position
    if player_stunned:
        # When player is stunned, ghost moves directly toward player and also moves forward
        target_ghost_x = player_x  # Move directly to player's x position
        ghost_target_y_offset = -20  # Move much closer to player (almost at player's position)
        
        # Move ghost horizontally toward player
        if ghost_x < target_ghost_x:
            ghost_x += ghost_chase_speed * 2  # Move faster when approaching stunned player
            if ghost_x > target_ghost_x:
                ghost_x = target_ghost_x
        elif ghost_x > target_ghost_x:
            ghost_x -= ghost_chase_speed * 2
            if ghost_x < target_ghost_x:
                ghost_x = target_ghost_x
        
        # Move ghost forward (closer in y direction)
        if ghost_y_offset < ghost_target_y_offset:
            ghost_y_offset += ghost_retreat_speed * 2  # Move forward faster
            if ghost_y_offset >= ghost_target_y_offset:
                ghost_y_offset = ghost_target_y_offset
                
        # Check if ghost has reached the player
        ghost_player_distance = abs(ghost_x - player_x) + abs(ghost_y_offset - (-20))
        if ghost_player_distance < 20:  # Ghost is very close to player
            print("The ghost has caught you!")
            print("GAME OVER!")
            print(f"Final Score: {score}")
            game_over = True
            
    else:
        # Normal ghost behavior when player is not stunned
        target_ghost_x = player_x + 30  # Target position is slightly to the side of player
        if ghost_x < target_ghost_x:
            ghost_x += ghost_chase_speed
            if ghost_x > target_ghost_x:  # Don't overshoot
                ghost_x = target_ghost_x
        elif ghost_x > target_ghost_x:
            ghost_x -= ghost_chase_speed
            if ghost_x < target_ghost_x:  # Don't overshoot
                ghost_x = target_ghost_x
        
        # Ghost hiding logic - move ghost further back gradually after 3 seconds (only when player not stunned and ghost not awakened)
        current_time = time.time()
        if not ghost_hidden and not ghost_awakened and current_time - game_start_time >= 3.0:
            # Start moving ghost gradually further back
            ghost_target_y_offset = -300  # Target position far behind
            ghost_hidden = True
            print("Ghost is retreating to the shadows...")
        
        # Gradually move ghost to target position (only if not awakened)
        if ghost_hidden and not ghost_awakened and ghost_y_offset > ghost_target_y_offset:
            ghost_y_offset -= ghost_retreat_speed  # Move back 5 units per frame
            if ghost_y_offset <= ghost_target_y_offset:
                ghost_y_offset = ghost_target_y_offset  # Don't overshoot
                print("Ghost has vanished into the darkness...")
        elif not ghost_hidden:
            # Keep ghost close during first 3 seconds
            ghost_hide_timer = current_time - game_start_time
    
    # Handle UFO system
    updateUFO()
    
    # Handle obstacles
    spawnObstacles()
    updateObstacles()
    checkCollisions()
    
    glutPostRedisplay()

def update_speed_progression():
    """
    Update player speed based on elapsed time
    Speed increases every 10 seconds up to a maximum limit
    """
    global player_speed, last_speed_increase_time, move_speed
    
    if game_paused or game_over or game_won:
        return  # Don't update speed when game is paused or ended
    
    current_time = time.time()
    elapsed_time = current_time - game_start_time
    
    # Check if it's time to increase speed
    if current_time - last_speed_increase_time >= speed_increase_interval:
        if player_speed < max_speed:
            old_speed = player_speed
            player_speed = min(player_speed + speed_increase_amount, max_speed)
            move_speed = player_speed  # Keep move_speed in sync
            last_speed_increase_time = current_time
            
            print(f"Speed increased! Time: {elapsed_time:.1f}s, Speed: {old_speed:.1f} -> {player_speed:.1f}")
        else:
            # Reset the timer even at max speed to avoid constant checking
            last_speed_increase_time = current_time
    
    # Also update obstacle spawn rate based on speed (faster = more obstacles)
    global obstacle_spawn_interval
    base_spawn_interval = 90
    speed_multiplier = player_speed / initial_speed
    obstacle_spawn_interval = max(int(base_spawn_interval / speed_multiplier), 30)  # Minimum 30 frames

def drawBackground():
    glClearColor(0.05, 0.05, 0.15, 1.0)  # Night sky color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def drawRoad():
    """
    Draw infinite road as one continuous strip using GL_QUADS
    """
    glColor3f(0.3, 0.3, 0.3)  # Road color
    
    # Create road points that extend well beyond visible area
    road_segments = 20  # Number of road segments
    segment_length = 100  # Length of each segment
    
    # Start road well before visible area and extend well beyond
    start_y = -1000 + (world_offset % segment_length)
    
    glBegin(GL_QUADS)
    
    for i in range(road_segments):
        y1 = start_y + i * segment_length
        y2 = start_y + (i + 1) * segment_length
        
        # Calculate road width at both points (perspective effect)
        # Far distance = narrow, close distance = wide
        progress1 = (y1 + 1000) / 2000.0  # 0 to 1 progression
        progress2 = (y2 + 1000) / 2000.0  # 0 to 1 progression
        
        left_x1 = -250 + progress1 * 150   # Goes from -250 to -100
        right_x1 = 250 - progress1 * 150   # Goes from 250 to 100
        left_x2 = -250 + progress2 * 150   # Goes from -250 to -100
        right_x2 = 250 - progress2 * 150   # Goes from 250 to 100
        
        # Draw quad for this road segment
        glVertex2f(left_x1, y1)   # Bottom left
        glVertex2f(right_x1, y1)  # Bottom right
        glVertex2f(right_x2, y2)  # Top right
        glVertex2f(left_x2, y2)   # Top left
    
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


def draw_bullet(bullet):
    if not bullet.active:
        return
        
    glPushMatrix()
    glTranslatef(bullet.loc[0], bullet.loc[1], bullet.loc[2])
    glColor3f(1, 0, 0)  # Red bullets like in reference
    glutSolidCube(7)    # Use cube like in reference
    glPopMatrix()
def shoot_bullet():
    global bullets, bullet_ammo, cheat_mode
    if cheat_mode or bullet_ammo > 0:  # Allow shooting if cheat mode is on OR has ammo
        bullets.append(CBullet(player_x, -250, player_z))  # Use correct player position
        if not cheat_mode:  # Only decrease ammo if not in cheat mode
            bullet_ammo -= 1  # Decrease ammo
            print(f"Bullet fired! Ammo remaining: {bullet_ammo}/5")
        else:
            print("Bullet fired! (Cheat mode - unlimited ammo)")
    else:
        print("No ammo! Collect yellow power-ups to get bullets.")
def update_bullets():
    global bullets, score
    
    # Update bullet positions
    for bullet in bullets:
        if bullet.active:
            bullet.update_position()
    
    # Check collisions
    check_bullet_hits()
    
    # Remove inactive bullets (like reference does)
    bullets = [b for b in bullets if b.active]

def check_bullet_hits():
    """Check if bullets hit obstacles - similar to reference check_hits()"""
    global score
    
    for bullet in bullets[:]:  # Use slice copy like reference
        if not bullet.active:
            continue
            
        for obstacle in obstacles[:]:  # Check against obstacles
            if not obstacle['active']:
                continue
                
            # Calculate distance between bullet and obstacle
            bx, by, bz = bullet.loc
            ox = obstacle['x']
            oy = obstacle['y'] + world_offset
            oz = 25  # Approximate obstacle height
            
            # Use distance calculation like reference
            distance = ((bx - ox)**2 + (by - oy)**2 + (bz - oz)**2)**0.5
            
            if distance < 40:  # Collision threshold
                if obstacle['type'] == 'tall' or obstacle['type'] == 'low':
                    # Destroy obstacle and bullet
                    obstacle['active'] = False
                    bullet.active = False
                    
                    # Add score for destroying obstacle
                    if obstacle['type'] == 'low':
                        score += 5
                        print("Bullet destroyed low obstacle! +5 score")
                    elif obstacle['type'] == 'tall':
                        score += 10
                        print("Bullet destroyed tall obstacle! +10 score")
                    
                    break  # Exit obstacle loop for this bullet
        
        # Remove bullets that go out of bounds (like reference)
        if abs(bullet.loc[0]) > X_MAX or bullet.loc[1] > Y_MAX:
            bullet.active = False

def createObstacle(obstacle_type, x_position):
    """
    Create different types of obstacles
    obstacle_type: 'low' (jump over), 'tall' (move left/right), or 'power' (collect)
    x_position: x position on the road (-150 to 150)
    """
    obstacle = {
        'type': obstacle_type,
        'x': x_position,
        'y': 400 - world_offset,  # Spawn ahead of current world position
        'active': True
    }
    
    # Add subtype for power-ups
    if obstacle_type == 'power':
        obstacle['subtype'] = random.choice(['green', 'yellow', 'silver'])
    
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
            glScalef(40, 40, 30)  # Wide, long, low
            glutSolidCube(1)
        elif obstacle['type'] == 'tall':
            # Tall obstacle - move left/right (blue color)
            glColor3f(0.0, 0.0, 1.0)  # Blue
            glTranslatef(0, 0, 80)  # Raise high above ground
            glScalef(40, 60, 120)  # Wide, long, tall
            glutSolidCube(1)
        elif obstacle['type'] == 'power':
            # Power-up with different colors based on subtype
            if 'subtype' in obstacle:
                if obstacle['subtype'] == 'green':
                    glColor3f(0.0, 1.0, 0.0)  # Green for score boost
                elif obstacle['subtype'] == 'yellow':
                    glColor3f(1.0, 1.0, 0.0)  # Yellow for ammo
                elif obstacle['subtype'] == 'silver':
                    glColor3f(0.8, 0.8, 0.8)  # Silver for extra life
                else:
                    glColor3f(0.0, 1.0, 0.0)  # Default green
            else:
                glColor3f(0.0, 1.0, 0.0)  # Default green for old system
            
            glTranslatef(0, 0, 20)    # Slightly above ground
            glScalef(20, 20, 20)      # Small cube
            glutSolidCube(1)
        glPopMatrix()  # Move this outside the elif block

def spawnObstacles():
    """
    Spawn new obstacles periodically at random positions across the road
    """
    global obstacle_spawn_timer
    
    obstacle_spawn_timer += 1
    
    if obstacle_spawn_timer >= obstacle_spawn_interval:
        obstacle_spawn_timer = 0
        
        # Randomly choose obstacle type
        obstacle_type = random.choice(['low', 'tall','power'])
        
        # Calculate road boundaries at player level (y = -250)
        # Road width calculation based on perspective effect from drawRoad()
        player_y = -250
        progress = (player_y + 1000) / 2000.0  # 0 to 1 progression
        road_left = -250 + progress * 150   # Left boundary at player level
        road_right = 250 - progress * 150   # Right boundary at player level
        
        # Random x position within road boundaries with some padding
        padding = 20  # Keep obstacles away from road edges
        x_position = random.randint(int(road_left + padding), int(road_right - padding))
        
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
        if obstacle['y'] + world_offset < -500:  # Remove when well past player
            obstacles_to_remove.append(obstacle)
    
    # Remove old obstacles
    for obstacle in obstacles_to_remove:
        obstacles.remove(obstacle)
        if len(obstacles_to_remove) > 0:  # Only print when actually removing
            print(f"Removed obstacle. Remaining obstacles: {len(obstacles)}")

def checkCollisions():
    """
    Check if player collides with any obstacles (simplified version)
    """
<<<<<<< HEAD
    global score, player_lives, bullet_ammo, game_over, low_obstacle_hits
    global player_stunned, ghost_hidden, ghost_y_offset, ghost_target_y_offset, ghost_awakened  # Add all needed ghost variables
=======
    global score, player_lives, bullet_ammo, game_over, silver_power_count
>>>>>>> f3e477cf980c6a43f5c9188fbf9ef8a0707a88d4
    player_size = 30  # Approximate player size
    
    for obstacle in obstacles:
        if not obstacle['active']:
            continue
            
        # Calculate obstacle position relative to world
        obs_x = obstacle['x']
        obs_y = obstacle['y'] + world_offset
        
        # Check if obstacle is near player's y position
        if abs(obs_y - (-250)) < 30:  # Player is at y = -250
            # Check x collision
            if abs(player_x - obs_x) < 30:  # Close in x direction
                if obstacle['type'] == 'low':
                    # Low obstacle - check if player is jumping high enough
                    if player_z < 80:  # Not jumping high enough
<<<<<<< HEAD
                        global low_obstacle_hits, ghost_hidden, ghost_y_offset, ghost_target_y_offset, ghost_awakened
                        low_obstacle_hits += 1
                        obstacle['active'] = False
                        
                        if low_obstacle_hits == 1:
                            # First hit - bring ghost back to initial position and permanently awaken it
                            print("Hit low obstacle! Ghost is awakening...")
                            ghost_hidden = False  # Make ghost visible again
                            ghost_awakened = True  # Permanently awaken ghost - it won't hide again
                            ghost_y_offset = -80  # Bring ghost back to initial close position
                            ghost_target_y_offset = -80  # Set target to close position
                            print("The ghost has returned from the shadows and will no longer hide!")
                            
                        elif low_obstacle_hits >= 2:
                            # Second hit - stun player and let ghost catch them
                            print("Hit low obstacle again! Player stunned, ghost is coming for you...")
                            player_stunned = True  # Stun player
                            print("You have awakened the ghost's wrath!")
                elif obstacle['type'] == 'tall':
                    # Tall obstacle - check if player is on ground (not jumping away)
                    if player_z <= ground_level + 10:  # On or near ground
                        print("Hit tall obstacle! Player stunned, ghost is approaching...")
                        player_stunned = True  # Stun player, don't end game yet
                        obstacle['active'] = False
=======
                        if silver_power_count > 0:
                            print(f"Hit low obstacle but PROTECTED by silver power! ({silver_power_count-1} remaining)")
                            score += 10  # Bonus points for surviving with silver power
                            silver_power_count -= 1  # Use one silver power
                            obstacle['active'] = False
                        else:
                            print("Hit low obstacle! Should have jumped!")
                            print("================================================")
                            print("                GAME OVER!")
                            print(f"              FINAL SCORE: {score}")
                            print("      Press 'R' to restart the game")
                            print("================================================")
                            game_over = True
                            obstacle['active'] = False
                elif obstacle['type'] == 'tall':
                    # Tall obstacle - check if player is on ground (not jumping away)
                    if player_z <= ground_level + 10:  # On or near ground
                        if silver_power_count > 0:
                            print(f"Hit tall obstacle but PROTECTED by silver power! ({silver_power_count-1} remaining)")
                            score += 10  # Bonus points for surviving with silver power
                            silver_power_count -= 1  # Use one silver power
                            obstacle['active'] = False
                        else:
                            print("Hit tall obstacle! Should have moved left/right!")
                            print("================================================")
                            print("                GAME OVER!")
                            print(f"              FINAL SCORE: {score}")
                            print("      Press 'R' to restart the game")
                            print("================================================")
                            game_over = True
                            obstacle['active'] = False
>>>>>>> f3e477cf980c6a43f5c9188fbf9ef8a0707a88d4
                elif obstacle['type'] == 'power':
                    # Power-up - collect it based on type
                    obstacle['active'] = False
                    print("Collected power-up!")
                    
                    # Check if obstacle has a subtype (for the old system power-ups)
                    if hasattr(obstacle, 'subtype') or 'subtype' in obstacle:
                        if obstacle['subtype'] == 'green':
                            # Green power-up increases score
                            score += 20
                            print("========================================")
                            print("COLLECTED GREEN POWER-UP! +20 SCORE!")
                            print(f"CURRENT SCORE: {score}")
                            print("========================================")
                        elif obstacle['subtype'] == 'silver':
                            # Silver power-up gives extra life AND protection power
                            if player_lives < 3:  
                                player_lives += 1
                                print(f"Collected SILVER power-up! Extra life! Lives: {player_lives}")
                            else:
                                print("Collected SILVER power-up! Already at max lives (3)")
                            
                            # Add silver protection power (max 3)
                            if silver_power_count < max_silver_power:
                                silver_power_count += 1
                                print(f"SILVER PROTECTION ADDED! Count: {silver_power_count}/{max_silver_power}")
                            else:
                                print(f"SILVER PROTECTION FULL! Already at max ({max_silver_power})")  
                        elif obstacle['subtype'] == 'yellow':
                            # Yellow power-up gives ammo (max 5 bullets)
                            if bullet_ammo < 5:
                                bullet_ammo += 1
                                print(f"Collected YELLOW power-up! Ammo: {bullet_ammo}/5")
                            else:
                                print("Collected YELLOW power-up! Already at max ammo (5/5)")


        

def restart_game():
    """
    Restart the game to initial state
    """
    global game_over, game_won, score, player_x, player_z, super_power_active, bullets
    global world_offset, player_velocity_z, is_jumping, obstacles
    global player_speed, game_start_time, last_speed_increase_time, move_speed, game_paused
<<<<<<< HEAD
    global player_lives, bullet_ammo, player_stunned, low_obstacle_hits  # Add low_obstacle_hits
    global ghost_x, ghost_y_offset, ghost_hide_timer, ghost_hidden, ghost_target_y_offset, ghost_awakened  # Add ghost variables
=======
    global player_lives, bullet_ammo, silver_power_count
>>>>>>> f3e477cf980c6a43f5c9188fbf9ef8a0707a88d4
    
    game_over = False
    game_won = False
    score = 0
    player_x = 0.0
    player_z = ground_level
    player_velocity_z = 0.0
    is_jumping = False
    world_offset = 0.0
    super_power_active = False
    silver_power_count = 0  # Reset silver power count
    bullets = []  # Clear all bullets
    obstacles = []
    game_paused = False
    player_lives = 3  # Reset lives
    bullet_ammo = 0   # Reset ammo
    player_stunned = False  # Reset stunned state
    low_obstacle_hits = 0  # Reset low obstacle hit counter
    
    # Reset ghost to initial position
    ghost_x = 30.0
    ghost_y_offset = -80  # Start close to player
    ghost_hide_timer = 0.0
    ghost_hidden = False
    ghost_awakened = False  # Reset awakened state
    ghost_target_y_offset = -80  # Reset target position
    
    # Reset speed progression
    player_speed = initial_speed
    move_speed = initial_speed
    game_start_time = time.time()
    last_speed_increase_time = game_start_time
    
    print("================================================")
    print("              GAME RESTARTED!")
    print(f"           Score: {score} | Lives: {player_lives}")
    print("     Collect GREEN obstacles for +20 score!")
    print("     Use arrow keys to move, SPACE to jump")
    print("================================================")

def check_super_power_activation():
    """
    Check if super power should be activated (e.g., after collecting certain power-ups)
    """
    global super_power_active, score
    
    # Activate super power every 100 points
    if score > 0 and score % 100 == 0 and not super_power_active:
        super_power_active = True
        print("Super power activated!")


def draw_text(x, y, text):
    """
    Draw text on screen (simplified version for console output)
    """
    # For now, just print to console since OpenGL text rendering is complex
    if text.startswith("Score:"):
        pass  # Don't spam score updates
    else:
        print(text)


    

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

def drawBorders():
    """
    Draw colorful borders using lines to define the game boundaries
    Players cannot go beyond these borders
    """
    # Set border color (bright cyan/blue) and line width
    glColor3f(0.0, 1.0, 1.0)  # Cyan color for visibility
    glLineWidth(8)  # Thicker lines for better visibility
    
    glBegin(GL_LINES)
    
    # Left border - extends along the entire visible road length
    for y_offset in range(-10, 11):  # Multiple segments for continuous border
        y_start = Y_MIN + y_offset * 200 + (world_offset % 200)
        y_end = y_start + 200
        
        # Left border line
        glVertex3f(X_MIN, y_start, Z_MIN)
        glVertex3f(X_MIN, y_start, Z_MAX)
        
        glVertex3f(X_MIN, y_start, Z_MAX)
        glVertex3f(X_MIN, y_end, Z_MAX)
        
        glVertex3f(X_MIN, y_end, Z_MAX)
        glVertex3f(X_MIN, y_end, Z_MIN)
        
        glVertex3f(X_MIN, y_end, Z_MIN)
        glVertex3f(X_MIN, y_start, Z_MIN)
        
        # Right border line  
        glVertex3f(X_MAX, y_start, Z_MIN)
        glVertex3f(X_MAX, y_start, Z_MAX)
        
        glVertex3f(X_MAX, y_start, Z_MAX)
        glVertex3f(X_MAX, y_end, Z_MAX)
        
        glVertex3f(X_MAX, y_end, Z_MAX)
        glVertex3f(X_MAX, y_end, Z_MIN)
        
        glVertex3f(X_MAX, y_end, Z_MIN)
        glVertex3f(X_MAX, y_start, Z_MIN)
    
    glEnd()
    
    # Reset line width to default
    glLineWidth(1)

def display():
    drawBackground()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Set up 3D perspective view
    gluLookAt(camera_x, camera_y, camera_z,    # Camera position
              look_x, look_y, look_z,          # Look at center
              0, 0, 1)                         # Up vector
    
    for bullet in bullets:
        draw_bullet(bullet)
    # Draw road
    drawRoad()
    # Draw road markings for animation visibility
    drawRoadMarkings()
    # Draw borders instead of buildings
    drawBorders()
    
    
    # Draw old-style obstacles for compatibility
    drawObstacles()
    
    
    # Draw 3D player in middle of road (player stays at center)
    drawPlayer()
    
    # Draw ghost chasing the player
    drawGhost()
    
    # Draw UFO
    drawUFO()
    
    # Draw UFO bullets
    for bullet in ufo_bullets:
        glPushMatrix()
        glTranslatef(bullet.loc[0], bullet.loc[2] + world_offset, bullet.loc[1])
        glColor3f(1.0, 0.0, 0.0)  # Red color for UFO bullets
        glScalef(0.5, 0.5, 0.5)
        glutSolidCube(1)
        glPopMatrix()
    
    # Display game state messages
    if game_over:
        draw_text(400, 400, "GAME OVER! Press R to restart")
    elif game_won:
        draw_text(400, 400, "YOU WON! Press R to play again")
    elif game_paused:
        draw_text(400, 400, "PAUSED - Press P to resume")
    
<<<<<<< HEAD
    # Print status info periodically
    if score % 50 == 0 or bullet_ammo != getattr(display, 'last_ammo', 0):
        cheat_status = " | CHEAT MODE ON" if cheat_mode else ""
        ammo_display = "∞" if cheat_mode else f"{bullet_ammo}/5"
        print(f"Score: {score} | Lives: {player_lives} | Ammo: {ammo_display}{cheat_status}")
=======
    # Display silver power status when player has power-ups
    if silver_power_count > 0:
        draw_text(400, 500, f"SILVER PROTECTION: {silver_power_count}/{max_silver_power}")
    
    # Print status info more frequently
    if score % 25 == 0 or bullet_ammo != getattr(display, 'last_ammo', 0) or score != getattr(display, 'last_score', 0):
        print(f"Score: {score} | Lives: {player_lives} | Ammo: {bullet_ammo}/5 | Silver: {silver_power_count}/{max_silver_power}")
>>>>>>> f3e477cf980c6a43f5c9188fbf9ef8a0707a88d4
        display.last_ammo = bullet_ammo
        display.last_score = score
    
    glutSwapBuffers()

def init():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, W_Width/W_Height, 0.1, 1000)  # 3D perspective projection

def main():
    global game_start_time, last_speed_increase_time
    
    glutInit()
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Added depth buffer
    glutCreateWindow(b"OpenGL City Draft")
    init()
    
    # Initialize game timing
    game_start_time = time.time()
    last_speed_increase_time = game_start_time

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(animate)  # Changed from display to animate
    glutMainLoop()

if __name__ == "__main__":
    main()
