from curse_snake import *
import curses
import time
from sys import argv


class SnakeDead(RuntimeError):
	pass


class SnakeGame():
	def __init__(self,infinite=False, start_speed=0.15, difficulty=20):
		self.snake = Snake(h=difficulty)
		self.infinite = infinite
		# initialize curses
		self.screen = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.screen.keypad(True)
		self.screen.leaveok(0)
		self.screen.nodelay(True)
		self.screen.border()
		self.snake.block(self.screen.getmaxyx())
		self.ticks = 0
		self.speed = start_speed
		self.growth = 1
		self.min_apples = 1
		self.points =0
		self.apple_char = "Q"
		self.blocking_char = 'X'

	def print_snake(self):
		if not self.infinite:
			self.screen.clear()
		self.screen.border()
		if len(self.snake.a) < self.min_apples:
			self.snake.apple(self.screen.getmaxyx())
		if self.snake.eat(self.growth):
			curses.beep()
			self.points = self.points + 10
		if self.snake.dead(self.screen.getmaxyx()):
			raise SnakeDead
		for i in range(self.snake.l):
			if i == 0: 
				char = DIRECTION[self.snake.d]
			else:
				char = '*'
			self.screen.addstr(self.snake.p[i].y,(self.snake.p[i].x*2),char)
		for i in range(len(self.snake.a)):
			self.screen.addstr(self.snake.a[i].y,(self.snake.a[i].x*2), self.apple_char)
		for i in range(len(self.snake.b)):
			self.screen.addstr(self.snake.b[i].y,(self.snake.b[i].x*2), self.blocking_char)
		self.screen.move(0,0)
		self.screen.refresh()

	def play(self):
		try:
			while True:
				self.print_snake()
				time.sleep(self.speed)
				key = self.screen.getch()
				if key == 97:
					self.snake.turn_left()
				elif key == 100:
					self.snake.turn_right()
				else:
					pass
				self.snake.move()
				self.ticks = self.ticks + 1
				if self.ticks % 177 == 0:
					self.speed = self.speed - .01
				if self.ticks % 223 == 0:
					self.growth = self.growth + 1
				if self.ticks % 453 == 0:
					self.min_apples = self.min_apples + 1
				self.points = self.points + self.min_apples
		
		except SnakeDead:
			message1 = 'OH NOOES!!!!!!'
			message2 = f"Your snake died with {self.points} points"
			message3 = 'Press any key to try again'
			message4 = 'Press CTRL+C to exit'
			midpoint = int(self.screen.getmaxyx()[1]/2)
			self.screen.addstr(5,midpoint-int(len(message1)/2),message1)
			self.screen.addstr(8,midpoint-int(len(message2)/2),message2)
			self.screen.addstr(14,midpoint-int(len(message4)/2),message4)
			self.screen.refresh()
		except KeyboardInterrupt:
			curses.nocbreak()
			self.screen.keypad(False)
			curses.echo()
			curses.endwin()
			quit()
		try:
			time.sleep(3)
			self.screen.addstr(11,midpoint-int(len(message3)/2),message3)
			self.screen.nodelay(False)
			key = self.screen.getch()
			if key:
				return True
		except KeyboardInterrupt:
			curses.nocbreak()
			self.screen.keypad(False)
			curses.echo()
			curses.endwin()
			quit()

if __name__ == '__main__':
	infinite = False
	speed=0.15
	difficulty = 20
	if len(argv) > 1:
		arg_index = 1
		if argv[arg_index] == '-h':
			print(f'Usage: {argv[0]} [infinite] [<speed>] (in milliseconds per move)')
			exit()
		if argv[arg_index] == 'infinite':
			infinite = True
			arg_index = arg_index + 1
		try: 
			speed = float(argv[arg_index])
			arg_index = arg_index + 1
		except ValueError:
			pass
		try: 
			difficulty = int(argv[arg_index])
		except ValueError:
			pass
	while True:
		game = SnakeGame(infinite=infinite, start_speed=speed, difficulty=difficulty)
		game.play()

