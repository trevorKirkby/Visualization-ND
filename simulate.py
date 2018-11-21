from warnings import filterwarnings
import numpy as np
import pygame

filterwarnings("ignore")

pygame.init()
clock = pygame.time.Clock()

info = pygame.display.Info()
size = min(info.current_w, info.current_h)
center = size / 2.

all_points = list()   #Represents hypercapsules centered on a given point.

def tunnel(start, end):
	return

class avatar:
	def __init__(self, loc, direct):
		self.loc = np.array(loc,dtype="int32")           #An N-dimensional point.
		self.vel = np.zeros([len(loc)],dtype="float32")  #An N-dimensional velocity vector.
		self.direct = np.array(direct,dtype="float64")   #A 2-dimensional vector of spherical coordinates of a unit vector.
		self.view = np.zeros([3,3],dtype="float64")      #A 3-dimensional vector of orthogonal 3-dimensional unit vectors.
		#self.screen = pygame.display.set_mode((size, size), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE)
		self.screen = pygame.display.set_mode((size, size))
		self.locked = 5
		pygame.mouse.set_visible(False)
		pygame.event.set_grab(True)
	def process_view(self):
		self.view[2] = np.array([np.cos(self.direct[1])*np.cos(self.direct[0]),
								np.sin(self.direct[1])*np.cos(self.direct[0]),
								np.sin(self.direct[0])])
		if (self.view[2] != (0, 1, 0)).any():
			self.view[1] = -np.cross(self.view[2], (0, 1, 0))
			self.view[1] /= np.sqrt(np.dot(self.view[1], self.view[1]))
		else:
			self.view[1] = np.array([np.cos(self.direct[1]), np.sin(self.direct[1]), 0])
		self.view[0] = -np.cross(self.view[2], self.view[1])
		try:
			assert abs(np.sqrt(np.dot(self.view[2], self.view[2])) - 1.) < 0.00001
			assert abs(np.sqrt(np.dot(self.view[1], self.view[1])) - 1.) < 0.00001
			assert abs(np.sqrt(np.dot(self.view[0], self.view[0])) - 1.) < 0.00001
		except AssertionError:
			print np.sqrt(np.dot(self.view[0], self.view[0])), np.sqrt(np.dot(self.view[1], self.view[1])), np.sqrt(np.dot(self.view[2], self.view[2]))
	def process_screen(self):
		self.screen.fill((255,255,255))
		projected = np.concatenate((all_points, np.zeros(len(all_points))[:,np.newaxis]), axis=1).astype("float32")
		projected[:,:-2] -= self.loc
		distance = (np.sqrt(np.einsum('...i,...i', projected[:,:3], projected[:,:3]))/center)
		projected[:,:3] = np.einsum("ji,ki->jk", projected[:,:3], self.view) #An annoyingly opaque but incredibly efficient means of projecting all the points in a single function call.
		projected[:,0] /= (projected[:,2]/center)
		projected[:,1] /= (projected[:,2]/center)
		projected[:,:2] += center
		projected[:,-1] = np.clip(10-np.clip(abs(projected[:,3])-projected[:,-2], 0, 30)/2, 0, 10)
		projected[:,-1] /= distance
		for point in projected.astype("int32"):
			if point[2] > 0 and point[-1] > 0:
				pygame.draw.circle(self.screen, (0,0,0), point[:2], point[-1])
		pygame.display.flip()
	def process_events(self):
		turn = pygame.mouse.get_rel()
		if self.locked:
			self.locked -= 1
		else:
			self.direct[0] -= (turn[1]/900.)
			self.direct[1] -= (turn[0]/900.)
			self.direct %= (2*np.pi)
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					raise SystemExit
				increment = 5
				if event.type == pygame.KEYUP: increment *= -1
				if event.key == pygame.K_d:
					self.vel[0] += increment
				if event.key == pygame.K_a:
					self.vel[0] -= increment
				if event.key == pygame.K_q:
					self.vel[1] += increment
				if event.key == pygame.K_e:
					self.vel[1] -= increment
				if event.key == pygame.K_w:
					self.vel[2] += increment
				if event.key == pygame.K_s:
					self.vel[2] -= increment
				if event.key == pygame.K_z:
					self.vel[3] += increment/5
				if event.key == pygame.K_x:
					self.vel[3] -= increment/5
	def process_movement(self):
		for e1,e2 in zip(self.vel[:3],self.view):
			self.loc[:3] += (e1*e2).astype("int32")
		self.loc[3:] += self.vel[3:].astype("int32")
	def process(self):
		self.process_events()
		self.process_movement()
		self.process_view()
		self.process_screen()

def run(camera):
	global all_points
	all_points = np.array(all_points)
	while True:
		clock.tick()
		camera.process()

all_points.append([50, 15, 15, 25, 100])
all_points.append([50, 35, 15, 25, 100])
all_points.append([50, 35, 35, 25, 100])
all_points.append([50, 15, 35, 25, 100])
run(avatar((25, 25, 25, 25), (0.0, 0.0)))
