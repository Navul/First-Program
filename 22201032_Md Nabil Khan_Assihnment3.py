from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time

# Assignment-specific variable names
camera_fov = 100
hero_pos = [0, 0, 0]
gun_angle = 0
camera_mode = "third"
fp_camera_angle = 0
tp_camera_distance = 500
tp_camera_height = 500
tp_camera_rotation = 0
cheat_mode = False
cheat_auto_follow = False
shots = []
foes = []
hero_lives = 5
missed_shots = 0
score = 0
game_over = False
foe_speed = 1
shot_speed = 5
step_toggle = False
cheat_fire_delay = 0.05
cheat_next_fire = 0
BOARD_SIZE = 500

# Initialize enemies
for _ in range(5):
	foes.append({
		'loc': [random.randint(-400, 400), 0, random.randint(-400, 400)],
		'scale': 1.0,
		'scale_dir': 0.01
	})

def render_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
	glColor3f(1,1,1)
	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	gluOrtho2D(0, 1000, 0, 800)
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()
	glRasterPos2f(x, y)
	for ch in text:
		glutBitmapCharacter(font, ord(ch))
	glPopMatrix()
	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	glMatrixMode(GL_MODELVIEW)

def render_hero():
	global step_toggle
	glPushMatrix()
	glTranslatef(hero_pos[0], hero_pos[1], hero_pos[2])
	# Lie down if game over
	if game_over:
		glRotatef(90, 0, 0, 1)  # Rotate around Z axis to lie down
	glPushMatrix()
	glRotatef(gun_angle, 0, 1, 0)

	# Draw body
	glPushMatrix()
	glTranslatef(0, 50, 0)
	glColor3f(0, 0.3, 0)
	glScalef(30, 60, 15)
	glutSolidCube(1)
	glPopMatrix()

	# Draw head
	glPushMatrix()
	glColor3f(0, 0, 0)
	glTranslatef(0, 90, 0)
	glutSolidSphere(12, 20, 20)
	glPopMatrix()

	# Draw hands and arms
	glPushMatrix()
	for side in [-1, 1]:
		glPushMatrix()
		glTranslatef(side * 10, 70, 5)
		glColor3f(0.9, 0.75, 0.65)
		glutSolidSphere(4, 10, 10)  # hand
		gluCylinder(gluNewQuadric(), 3, 3, 35, 10, 10)  # arm
		glPopMatrix()

	# Draw gun
	glPushMatrix()
	glTranslatef(0, 70 , 0)
	glColor3f(0.5, 0.5, 0.5)
	gluCylinder(gluNewQuadric(), 2.5, 2.5, 40, 10, 10)
	glPopMatrix()
	glPopMatrix()

	# Draw legs
	leg_angle = 0
	leg_len = 40
	leg_pos = [(-12, 20, 0), (12, 20, 0)]
	glColor3f(0, 0, .5)
	for i, pos in enumerate(leg_pos):
		glPushMatrix()
		glTranslatef(pos[0], pos[1], pos[2])
		tilt = leg_angle if (i == 0 and step_toggle) or (i == 1 and not step_toggle) else -leg_angle
		glRotatef(90 + tilt, 1, 0, 0)
		gluCylinder(gluNewQuadric(), 3, 3, leg_len, 10, 10)
		glPopMatrix()
	glPopMatrix()
	glPopMatrix()

def render_foe(foe):
	glPushMatrix()
	glTranslatef(foe['loc'][0], 30, foe['loc'][2])
	glScalef(foe['scale'], foe['scale'], foe['scale'])
	glColor3f(1, 0, 0)
	glutSolidSphere(30, 20, 20)
	glTranslatef(0, 40, 0)
	glColor3f(0, 0, 0)
	glutSolidSphere(15, 20, 20)
	glPopMatrix()

def render_shot(shot):
	glPushMatrix()
	glTranslatef(shot['loc'][0], shot['loc'][1], shot['loc'][2])
	glColor3f(1, 0, 0)
	glutSolidCube(7)
	glPopMatrix()

def render_board():
	tile = 50
	for x in range(-BOARD_SIZE, BOARD_SIZE, tile):
		for z in range(-BOARD_SIZE, BOARD_SIZE, tile):
			glColor3f(1, 1, 1) if ((x + z) // tile) % 2 == 0 else glColor3f(0.8, 0.6, 0.9)
			glBegin(GL_QUADS)
			glVertex3f(x, 0, z)
			glVertex3f(x + tile, 0, z)
			glVertex3f(x + tile, 0, z + tile)
			glVertex3f(x, 0, z + tile)
			glEnd()

def render_boundaries():
	wall_h = 50
	def wall_face(rgb, corners):
		glColor3f(*rgb)
		glBegin(GL_QUADS)
		for corner in corners:
			glVertex3f(*corner)
		glEnd()
	s = BOARD_SIZE
	wall_face((0,0,1), [(-s,0,-s),(-s,wall_h,-s),(-s,wall_h,s),(-s,0,s)])
	wall_face((1,1,1), [(-s,0,s),(-s,wall_h,s),(s,wall_h,s),(s,0,s)])
	wall_face((0,1,0), [(s,0,s),(s,wall_h,s),(s,wall_h,-s),(s,0,-s)])
	wall_face((0,1,1), [(s,0,-s),(s,wall_h,-s),(-s,wall_h,-s),(-s,0,-s)])

def key_handler(key, x, y):
	global gun_angle, cheat_mode, cheat_auto_follow, game_over, hero_lives, missed_shots, score, step_toggle, hero_pos
	key = key.decode('utf-8').lower()
	if game_over and key == 'r':
		game_over = False
		hero_lives, missed_shots, score = 5, 0, 0
		hero_pos[:] = [0, 0, 0]
		foes.clear()
		for _ in range(5):
			foes.append({'loc': [random.randint(-400, 400), 0, random.randint(-400, 400)], 'scale': 1.0, 'scale_dir': 0.01})
		shots.clear()
		# Reset cheat mode flags
		global cheat_mode, cheat_auto_follow
		cheat_mode = False
		cheat_auto_follow = False
		return

	move = {'w': 10, 's': -10}.get(key, 0)
	if move:
		dx = math.sin(math.radians(gun_angle)) * move
		dz = math.cos(math.radians(gun_angle)) * move
		hero_pos[0] += dx
		hero_pos[2] += dz
		step_toggle = not step_toggle
	elif key == 'a': gun_angle += 5
	elif key == 'd': gun_angle -= 5
	elif key == 'c': 
		cheat_mode = not cheat_mode
	elif key == 'v' and cheat_mode: 
		cheat_auto_follow = not cheat_auto_follow
		if cheat_auto_follow:
			fp_camera_angle = gun_angle

def special_key_handler(key, x, y):
	global tp_camera_height, tp_camera_rotation
	tp_camera_height += 10 if key == GLUT_KEY_UP else -10 if key == GLUT_KEY_DOWN else 0
	tp_camera_rotation += 5 if key == GLUT_KEY_LEFT else -5 if key == GLUT_KEY_RIGHT else 0
	tp_camera_height = max(100, min(tp_camera_height, 1500))
	tp_camera_rotation %= 360

def mouse_handler(button, state, x, y):
	global camera_mode, fp_camera_angle
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
		shots.append({'loc': hero_pos[:], 'dir': [math.sin(math.radians(gun_angle)), 0, math.cos(math.radians(gun_angle))], 'active': True})
	elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
		if camera_mode == "third":
			camera_mode = "first"
			fp_camera_angle = gun_angle
		else:
			camera_mode = "third"

def setup_camera():
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(camera_fov, 1.25, 0.1, 1500)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	if camera_mode == "third":
		cam_x = hero_pos[0] + math.sin(math.radians(tp_camera_rotation)) * tp_camera_distance
		cam_z = hero_pos[2] + math.cos(math.radians(tp_camera_rotation)) * tp_camera_distance
		look_y = max(hero_pos[1] + 100, hero_pos[1] + tp_camera_height * 0.1)
		gluLookAt(cam_x, tp_camera_height, cam_z, 
				  hero_pos[0], look_y, hero_pos[2],
				  0, 1, 0)
	else:
		cam_x = hero_pos[0] + math.sin(math.radians(fp_camera_angle)) * 20
		cam_z = hero_pos[2] + math.cos(math.radians(fp_camera_angle)) * 20
		gluLookAt(cam_x, 100, cam_z, 
				  cam_x + math.sin(math.radians(fp_camera_angle)) * 100, 50, cam_z + math.cos(math.radians(fp_camera_angle)) * 100, 
				  0, 1, 0)

def check_hits():
	global score, hero_lives, missed_shots, game_over
	for shot in shots[:]:
		for foe in foes[:]:
			sx, sy, sz = shot['loc']
			ex, ey, ez = foe['loc'][0], 30, foe['loc'][2]
			if math.dist([sx, sy, sz], [ex, ey, ez]) < 50:
				score += 10
				foe['loc'][0], foe['loc'][2] = random.randint(-400, 400), random.randint(-400, 400)
				shots.remove(shot)
				break
		if abs(shot['loc'][0]) > BOARD_SIZE or abs(shot['loc'][2]) > BOARD_SIZE:
			missed_shots += 1
			shots.remove(shot)
			if missed_shots >= 10:
				game_over = True
	for foe in foes:
		if math.dist([hero_pos[0], 0, hero_pos[2]], [foe['loc'][0], 30, foe['loc'][2]]) < 50:
			hero_lives -= 1
			foe['loc'][0], foe['loc'][2] = random.randint(-400, 400), random.randint(-400, 400)
			if hero_lives <= 0:
				game_over = True

def update_foes():
	for foe in foes:
		dx = hero_pos[0] - foe['loc'][0]
		dz = hero_pos[2] - foe['loc'][2]
		dist = math.sqrt(dx**2 + dz**2)
		if dist > 0:
			foe['loc'][0] += (dx/dist) * foe_speed
			foe['loc'][2] += (dz/dist) * foe_speed
		foe['scale'] += foe['scale_dir']
		if foe['scale'] > 1.2 or foe['scale'] < 0.8:
			foe['scale_dir'] *= -1

def update_shots():
	for shot in shots:
		shot['loc'][0] += shot['dir'][0] * shot_speed
		shot['loc'][2] += shot['dir'][2] * shot_speed

def idle_func():
	global gun_angle, cheat_next_fire, cheat_fire_delay, fp_camera_angle
	if not game_over:
		if cheat_mode:
			gun_angle = (gun_angle + 2)
			now = time.time()
			if foe_in_sight() and now >= cheat_next_fire:
				fire_shot()
				cheat_next_fire = now + cheat_fire_delay
		if camera_mode == "first":
			if cheat_mode and cheat_auto_follow:
				fp_camera_angle = gun_angle
		update_foes()
		update_shots()
		check_hits()
	glutPostRedisplay()

def foe_in_sight():
	tolerance = 5
	for foe in foes:
		dx = foe['loc'][0] - hero_pos[0]
		dz = foe['loc'][2] - hero_pos[2]
		angle_to_foe = math.degrees(math.atan2(dx, dz)) % 360
		gun_mod = gun_angle % 360
		if abs((angle_to_foe - gun_mod + 180) % 360 - 180) < tolerance:
			return True
	return False

def fire_shot():
	shots.append({
		'loc': hero_pos[:],
		'dir': [math.sin(math.radians(gun_angle)), 0, math.cos(math.radians(gun_angle))],
		'active': True
	})

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glViewport(0, 0, 1000, 800)
	setup_camera()
	render_board()
	render_boundaries()
	render_hero()
	for foe in foes: render_foe(foe)
	for shot in shots: render_shot(shot)
	render_text(10, 770, f"Hero Life Remaining {hero_lives} ")
	render_text(10,745,f"Game Score: {score}")
	render_text(10,720,f"Bullets Missed: {missed_shots}")
	if game_over:
		render_text(400, 600, f"GAME OVER. Score: {score}")
		render_text(460, 575, 'Press "R" to restart')
	glutSwapBuffers()

def main():
	glutInit()
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize(1000, 800)
	glutInitWindowPosition(0,0)
	glutCreateWindow(b"Bullet Frenzy Assignment Game")
	glEnable(GL_DEPTH_TEST)
	glutDisplayFunc(display)
	glutKeyboardFunc(key_handler)
	glutSpecialFunc(special_key_handler)
	glutMouseFunc(mouse_handler)
	glutIdleFunc(idle_func)
	glutMainLoop()

if __name__ == "__main__":
	main()
