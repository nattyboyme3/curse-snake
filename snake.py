from curse_snake import *
import curses
import time
from sys import argv
import csv
import os

KEYS = [
    (119, 87, curses.KEY_UP),
    (100, 68, curses.KEY_RIGHT),
    (115, 83, curses.KEY_DOWN),
    (97, 65, curses.KEY_LEFT),
]


class SnakeDead(RuntimeError):
    pass

def clear_pause(screen):
    key = 1
    time.sleep(1)
    screen.nodelay(True)
    while key != -1:
        key = screen.getch()
    screen.nodelay(False)
    # pause for input
    key = screen.getch()

class SnakeGame():
    def __init__(self, is_simple=True, is_infinite=False, start_speed=0.3, walls=10):
        self.snake = Snake(h=walls)
        self.walls = walls
        self.infinite = is_infinite
        self.simple = is_simple
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
        self.fast = False
        self.ticks = 0
        self.speed = start_speed
        self.growth = 1
        self.min_apples = 1
        self.points = float(0)
        self.apple_char = "Q"
        self.blocking_char = 'X'
        self.score_file = '.snake_scores.csv'
        self.score_fields = ['initials', 'score']
        self.high_scores = []
        self.lost = False

    def get_scores(self):
        scores = []
        with open(self.score_file,"r", newline='') as csv_file:
            score_reader = csv.DictReader(csv_file)
            for row in score_reader:
                scores.append(row)
        return scores

    def add_score(self, initials, score):
        decoded_initials = initials.decode("utf-8")
        if os.path.exists(self.score_file):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not
        with open(self.score_file, append_write, newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.score_fields)
            if append_write == 'w':
                writer.writeheader()
            writer.writerow({self.score_fields[0]: decoded_initials, self.score_fields[1]: score})


    def countdown(self):
        maxes = self.screen.getmaxyx()
        countdown_window = curses.newwin(5, 20, 4, int(maxes[1]/2)-10)
        countdown_window.bkgdset(' ', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.bkgd(' ', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.border()
        countdown_window.addstr(1, 5, 'GET READY!', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.refresh()
        countdown = 3
        while countdown > 0:
            countdown_string = ' ...' + str(countdown) + '... '
            countdown_window.addstr(2, 6, str(countdown_string), curses.color_pair(4) | curses.A_BOLD)
            countdown_window.move(0, 0)
            countdown_window.refresh()
            countdown = countdown - 1
            time.sleep(1)
        countdown_window.move(0, 0)

    def pause(self):
        maxes = self.screen.getmaxyx()
        pause_window = curses.newwin(5, 22, 4, int(maxes[1]/2)-10)
        pause_window.bkgdset(' ', curses.color_pair(4) | curses.A_BOLD)
        pause_window.bkgd(' ', curses.color_pair(4) | curses.A_BOLD)
        pause_window.border()
        pause_window.addstr(2, 3, 'GAME IS PAUSED')
        pause_window.refresh()
        pause_window.move(0, 0)
        key = -1
        while key != 32:
            key = self.screen.getch()

    def game_over(self):
        maxes = self.screen.getmaxyx()
        score_window = curses.newwin(19, 40, 4, int(maxes[1] / 2) - 20)
        score_window.bkgdset(' ', curses.color_pair(4))
        score_window.bkgd(' ', curses.color_pair(4))
        score_window.border()
        midpoint = int(score_window.getmaxyx()[1] / 2)
        message4 = 'Press CTRL+C to exit'
        continue_message = 'Press any key to continue...'
        if self.lost:
            message1 = 'OH NOOES!!!!!!'
            message2 = f"Your snake died with {int(self.points)} points"
            message3 = "Enter your initials: "
        else:
            message1 = 'Congratulations!!!!'
            message2 = f'You finished level <number> with {int(self.points)} points'
            message3 = ''
        score_window.addstr(2, midpoint - int(len(message1) / 2), message1, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(4, midpoint - int(len(message2) / 2), message2, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(14, midpoint - int(len(message4) / 2), message4, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(6, midpoint - int(len(continue_message) / 2), continue_message, curses.color_pair(4))
        score_window.refresh()
        # make sure no stray keys are picked up
        clear_pause(score_window)

        if self.lost:
            # get real input
            curses.echo()
            curses.nocbreak()
            score_window.clear()
            message5 = "HIGH SCORES"
            score_window.addstr(2, midpoint - int(len(message5) / 2), message5, curses.color_pair(4) | curses.A_BOLD)
            score_window.addstr(6, midpoint - int(len(message3) / 2)-4, message3, curses.color_pair(4))
            score_window.refresh()
            initials = score_window.getstr(3)
            curses.noecho()
            curses.cbreak()
            score_window.clear()
            score_window.addstr(2, midpoint - int(len(message5) / 2), message5, curses.color_pair(4) | curses.A_BOLD)
            self.add_score(initials, int(self.points))
            self.high_scores = self.get_scores()

            sorted_scores = sorted(self.high_scores, key=lambda item: int(item['score']), reverse=True)
            for i in range(10):
                if len(sorted_scores) > i:
                    score_line = f'{i+1} - {sorted_scores[i][self.score_fields[0]]}:' + \
                                 f' \t {sorted_scores[i][self.score_fields[1]]}'
                    score_window.addstr(4+i, midpoint - 7, score_line, curses.color_pair(4))
            score_window.refresh()
            time.sleep(1)
            score_window.addstr(15, midpoint - int(len(continue_message) / 2), continue_message,
                                curses.color_pair(4))
            score_window.addstr(17, midpoint - int(len(message4) / 2), message4, curses.color_pair(4) | curses.A_BOLD)
            score_window.refresh()
            clear_pause(score_window)

        return not self.lost

    def print_snake(self):
        maxes = self.screen.getmaxyx()
        if not self.infinite:
            self.screen.clear()
        self.screen.border()
        if len(self.snake.a) < self.min_apples:
            self.snake.apple(maxes)
        if self.snake.eat(self.growth):
            curses.beep()
            self.points = self.points + self.walls
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
            self.countdown()
            while True:
                self.print_snake()
                if self.fast:
                    time.sleep(self.speed/4)
                    key = 999
                    last_key = -1
                    while key != -1:
                        last_key = key
                        key = self.screen.getch()
                    key = last_key
                else:
                    time.sleep(self.speed)
                    key = self.screen.getch()
                if self.simple:
                    if key == 97 or key == 65 or key == curses.KEY_LEFT:
                        self.snake.turn_left()
                    elif key == 100 or key == 68 or key == curses.KEY_RIGHT:
                        self.snake.turn_right()
                else:
                    if key in KEYS[3]:
                        if self.snake.d == 3:
                            self.fast = True
                        else:
                            self.fast = False
                        if not self.snake.d == 1:
                            self.snake.d = 3
                    elif key in KEYS[1]:
                        if self.snake.d == 1:
                            self.fast = True
                        else:
                            self.fast = False
                        if not self.snake.d == 3:
                            self.snake.d = 1
                    elif key in KEYS[2]:
                        if self.snake.d == 2:
                            self.fast = True
                        else:
                            self.fast = False
                        if not self.snake.d == 0:
                            self.snake.d = 2
                    elif key in KEYS[0]:
                        if self.snake.d == 0:
                            self.fast = True
                        else:
                            self.fast = False
                        if not self.snake.d == 2:
                            self.snake.d = 0
                    elif key == 32:
                        self.pause()
                    else:
                        self.fast = False
                self.snake.move()
                self.ticks = self.ticks + 1
                if self.ticks % 103 == 0:
                    self.speed = self.speed - .01
                if self.ticks % 343 == 0:
                    self.growth = self.growth + 1
                if self.ticks % 198 == 0:
                    self.min_apples = self.min_apples + 1
                self.points = self.points + (1 - self.speed)

        except SnakeDead:
            self.lost = True
        return self.game_over()

if __name__ == '__main__':
    infinite = False
    speed=0.3
    difficulty = 10
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
