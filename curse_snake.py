import copy
import time
import random

random.seed(time.time())

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DIRECTION = ['^', '>', 'V', '<']

class Position():
	def __init__(self, y=0, x=0):
		self.x = x
		self.y = y

	def move(self, d,s=1):
		if d == NORTH:
			self.y = self.y - s
		if d == EAST:
			self.x = self.x + s
		if d == SOUTH:
			self.y = self.y + s
		if d == WEST:
			self.x = self.x - s

	def __repr__(self):
		return '(' + str(self.x) + ',' + str(self.y) + ')'


class Snake: 
	def __init__(self, y=10, x=10, h=20):
		self.l = 5
		self.h = h
		self.d = NORTH
		self.p = [Position(y=y,x=x)]
		self.a = [Position(y=y+2, x=x+2)]
		self.b = []
		for i in range(self.l): 
			n = copy.deepcopy(self.p[i])
			n.move(SOUTH)
			self.p.append(n)


	def turn(self, r=True):
		if r == True:
			self.d = ( self.d + 1 ) % 4
		else: 
			self.d = ( self.d - 1 ) % 4

	def turn_left(self):
		self.turn(False)

	def turn_right(self):
		self.turn(True)

	def grow(self, x):
		for i in range(x):
			self.p.append(copy.deepcopy(self.p[self.l-1]))
		self.l = self.l + x

	def move(self):
		prv = copy.deepcopy(self.p[0])
		self.p[0].move(self.d)
		for i in range(1,self.l+1):
			nxt = self.p[i]
			self.p[i] = prv
			prv = nxt

	def dead(self, maxes):
		h = self.p[0]
		for i in range(1,self.l):
			if self.p[i].x == h.x and self.p[i].y == h.y:
				return True
		if h.x <= 0 or h.y <= 0:
			return True
		if h.x*2 >= maxes[1]-1 or h.y >= maxes[0]-1:
			return True
		for i in self.b:
			if h.x == i.x and h.y == i.y:
				return True
		return False

	def apple(self, maxes):
		spawned = False
		while not spawned:
			spawned = True
			y = random.randint(1,maxes[0]-2)
			x = random.randint(1,int(maxes[1]/2)-2)
			for i in self.b:
				if i.x == x and i.y == y:
					spawned = False
					break
		self.a.append(Position(y,x))

	def eat(self, growth):
		h = self.p[0]
		for i in self.a:
			if h.x == i.x and h.y == i.y:
				self.grow(growth)
				self.a.remove(i)
				return True

	def block(self, maxes):
		for i in range(self.h):
			y = random.randint(1,maxes[0]-2)
			x = random.randint(1,int(maxes[1]/2)-2)
			length = random.randint(3,7)
			direction = random.randint(0,3)
			if x == 10 and (y >= 10 and y <=15):
				continue
			wall = Position(y,x)
			self.b.append(wall)
			for j in range(length):
				next_wall = copy.deepcopy(wall)
				next_wall.move(direction)
				if not (next_wall.y > (maxes[0]-2) or 
						(next_wall.x*2) > (maxes[1]-2) or
						next_wall.x <= 1 or
						next_wall.y <= 1):
					if x == 10 and (y >= 2 and y <=20):
						continue
					self.b.append(next_wall)
					wall = next_wall
				else:
					continue
			if x == 10 and (y >= 10 and y <=15):
				continue

	def __repr__(self):
		r = ''
		m = []
		for x in range(30):
			m.append(list())
			for y in range(30):
				m [x].append('   ')
		for s in range (self.l):
			if s == 0:
				m[self.p[s].x][self.p[s].y] = ' ' + DIRECTION[self.d] + ' '
			else:
				m[self.p[s].x][self.p[s].y] = ' * '

		for x in range(30):
			for y in range(30):
				r = r + m[y][x]
			r = r + '|\n'
		return r



	
