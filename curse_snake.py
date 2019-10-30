import copy
import time
import random

random.seed(time.time())

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIRECTION = ['^', '>', 'V', '<']


class Position():
    def __init__(self, y=0, x=0):
        self.x = x
        self.y = y

    def move(self, d,s=1):
        if d == UP:
            self.y = self.y - s
        if d == RIGHT:
            self.x = self.x + s
        if d == DOWN:
            self.y = self.y + s
        if d == LEFT:
            self.x = self.x - s

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'


class Snake:
    def __init__(self, y=10, x=10, h=20):
        self.l = 5
        self.h = h
        self.d = UP
        self.p = [Position(y=y,x=x)]
        self.a = [Position(y=y+2, x=x+2)]
        self.b = []
        for i in range(self.l):
            n = copy.deepcopy(self.p[i])
            n.move(DOWN)
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
        while True:
            y = random.randint(1,maxes[0]-2)
            x = random.randint(1,int(maxes[1]/2)-2)
            new_apple = Position(y,x)
            for wall in self.b:
                if wall == new_apple:
                    new_apple = False
                    break
            if new_apple:
                self.a.append(Position(y,x))
                break

    def eat(self, growth):
        h = self.p[0]
        for i in self.a:
            if h.x == i.x and h.y == i.y:
                self.grow(growth)
                self.a.remove(i)
                return True

    def wall(self, maxes):
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
                    if next_wall.x == 10 and (next_wall.y <=15 and next_wall.y >= 5) :
                        continue
                    self.b.append(next_wall)
                    wall = next_wall
                else:
                    continue
            if x == 10 and (y >= 10 and y <=15):
                continue



