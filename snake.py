from curse_snake import *
import curses
import time
from sys import argv


class SnakeDead(RuntimeError):
    pass


class SnakeGame():
    def __init__(self, is_simple=True, is_infinite=False, start_speed=0.15, walls=20):
        self.snake = Snake(h=walls)
        self.infinite = is_infinite
        self.simple = is_simple
        # initialize curses
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.leaveok(0)
        self.screen.nodelay(True)
        self.screen.border()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self.snake.wall(self.screen.getmaxyx())
        self.ticks = 0
        self.speed = start_speed
        self.growth = 1
        self.min_apples = 1
        self.points =0
        self.apple_char = "Q"
        self.blocking_char = 'X'

    def print_snake(self):
        maxes = self.screen.getmaxyx()
        if not self.infinite:
            self.screen.clear()
        self.screen.border()
        if len(self.snake.a) < self.min_apples:
            self.snake.apple(maxes)
        if self.snake.eat(self.growth):
            curses.beep()
            self.points = self.points + 10
        if self.snake.dead(maxes):
            raise SnakeDead
        for i in range(self.snake.l):
            if i == 0:
                char = DIRECTION[self.snake.d]
            else:
                char = '*'
            self.screen.addstr(self.snake.p[i].y,(self.snake.p[i].x*2),char)
        for i in range(len(self.snake.a)):
            self.screen.addstr(	self.snake.a[i].y,(self.snake.a[i].x*2),
                                self.apple_char, curses.color_pair(2) | curses.A_BOLD)
        for i in range(len(self.snake.b)):
            self.screen.addstr(	self.snake.b[i].y,(self.snake.b[i].x*2),
                                self.blocking_char, curses.color_pair(3) | curses.A_BOLD)
        self.screen.move(0,0)
        self.screen.refresh()

    def play(self):
        try:
            self.print_snake()
            start_message = "   GET READY!!   "
            midpoint = int(self.screen.getmaxyx()[1] / 2)
            self.screen.addstr(5, midpoint - int(len(start_message) / 2), start_message,
                               curses.color_pair(4) | curses.A_BOLD)
            countdown = 3
            while countdown > 0:
                countdown_string = ' ...' + str(countdown) + '... '
                self.screen.addstr(6, midpoint - int(len(countdown_string) / 2), str(countdown_string),
                                   curses.color_pair(4) | curses.A_BOLD)
                self.screen.move(0, 0)
                self.screen.refresh()
                countdown = countdown - 1
                time.sleep(1)
            while True:
                self.print_snake()
                time.sleep(self.speed)
                key = self.screen.getch()
                if self.simple:
                    if key == 97 or key == 65 or key == curses.KEY_LEFT:
                        self.snake.turn_left()
                    elif key == 100 or key == 68 or key == curses.KEY_RIGHT:
                        self.snake.turn_right()
                else:
                    if key == 97 or key == 65 or key == curses.KEY_LEFT:
                        if not self.snake.d == 1:
                            self.snake.d = 3
                    elif key == 100 or key == 68 or key == curses.KEY_RIGHT:
                        if not self.snake.d == 3:
                            self.snake.d = 1
                    elif key == 115 or key == 83 or key == curses.KEY_DOWN:
                        if not self.snake.d == 0:
                            self.snake.d = 2
                    elif key == 119 or key == 87 or key == curses.KEY_UP:
                        if not self.snake.d == 2:
                            self.snake.d = 0
                    elif key == 32:
                        self.screen.nodelay(False)
                        midpoint = int(self.screen.getmaxyx()[1] / 2)
                        paused = '   GAME IS PAUSED   '
                        twenty_spaces = '                    '
                        self.screen.addstr(4, midpoint - int(len(twenty_spaces) / 2), twenty_spaces,
                                           curses.color_pair(4) | curses.A_BOLD)
                        self.screen.addstr(5, midpoint - int(len(paused) / 2), paused,
                                           curses.color_pair(4) | curses.A_BOLD)
                        self.screen.addstr(6, midpoint - int(len(twenty_spaces) / 2), twenty_spaces,
                                           curses.color_pair(4) | curses.A_BOLD)
                        self.screen.move(0, 0)
                        self.screen.refresh()
                        key = -1
                        while key != 32:
                            key = self.screen.getch()
                        self.screen.nodelay(True)
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
        time.sleep(3)
        key = 1
        while key != -1:
            key = self.screen.getch()
        self.screen.addstr(11,midpoint-int(len(message3)/2),message3)
        self.screen.nodelay(False)
        key = self.screen.getch()
        if key:
            return True


if __name__ == '__main__':
    infinite = False
    speed=0.15
    difficulty = 20
    simple = False
    if len(argv) > 1:
        arg_index = 1
        if argv[arg_index] == '-h':
            print(f'Usage: {argv[0]} [infinite] [<speed>] (in milliseconds per move)')
            exit()
        if argv[arg_index] == 'simple':
            simple = True
            arg_index = arg_index + 1
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
        game = SnakeGame(is_simple=simple, is_infinite=infinite, start_speed=speed, walls=difficulty)
        try:
            game.play()
        except KeyboardInterrupt:
            curses.nocbreak()
            game.screen.keypad(False)
            curses.echo()
            curses.endwin()
            quit()
