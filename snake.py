from libsnake import *
import curses
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
    def __init__(self, is_simple=False, start_speed=0.3, walls=10, points=0, level=1, level_up=400):
        self.snake = Snake(h=walls)
        self.walls = walls
        self.simple = is_simple
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(True)
        self.screen.leaveok(0)
        self.screen.nodelay(True)
        self.screen.border()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self.fast = False
        self.ticks = 0
        self.speed = start_speed
        self.growth = 1
        self.min_apples = 1
        self.points = float(points)
        self.level = level
        self.apple_char = "Q"
        self.blocking_char = 'X'
        self.score_file = '.snake_scores.csv'
        self.score_fields = ['initials', 'score','level']
        self.high_scores = []
        self.start_points = points
        self.start_speed = start_speed
        self.lost = False
        self.display_scores = True
        self.level_up = level_up

    def get_scores(self):
        scores = []
        if os.path.exists(self.score_file):
            with open(self.score_file,"r", newline='') as csv_file:
                score_reader = csv.DictReader(csv_file)
                for row in score_reader:
                    scores.append(row)
        else:

            for j in range(10):
                score = {}
                for i in self.score_fields:
                    score[i]='0'
                scores.append(score)
        return scores

    def add_score(self, initials, score, level):
        decoded_initials = initials.decode("utf-8")
        if os.path.exists(self.score_file):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not
        with open(self.score_file, append_write, newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.score_fields)
            if append_write == 'w':
                writer.writeheader()
            writer.writerow({self.score_fields[0]: decoded_initials,
                             self.score_fields[1]: score,
                             self.score_fields[2]: level
                             })

    def countdown(self):
        maxes = self.screen.getmaxyx()
        countdown_window = curses.newwin(10, 25, int(maxes[0]/2)-5, int(maxes[1]/2)-10)
        countdown_window.bkgdset(' ', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.bkgd(' ', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.border()
        countdown_window.addstr(1, 7, 'GET READY! ', curses.color_pair(4) | curses.A_BOLD)
        countdown_window.addstr(4, 4, 'Move:   Arrow Keys', curses.color_pair(4))
        countdown_window.addstr(5, 4, '        or WASD', curses.color_pair(4))
        countdown_window.addstr(6, 4, 'Pause:  Space', curses.color_pair(4))
        countdown_window.addstr(7, 4, 'Exit:   Ctrl + C', curses.color_pair(4))

        countdown_window.refresh()
        countdown = 3
        while countdown > 0:
            countdown_string = ' ...' + str(countdown) + '... '
            countdown_window.addstr(2, 8, str(countdown_string), curses.color_pair(4) | curses.A_BOLD)
            countdown_window.move(0, 0)
            countdown_window.refresh()
            countdown = countdown - 1
            time.sleep(1)
        countdown_window.move(0, 0)

    def pause(self):
        maxes = self.screen.getmaxyx()
        pause_window = curses.newwin(4, 22, 4, int(maxes[1]/2)-10)
        pause_window.bkgdset(' ', curses.color_pair(4) | curses.A_BOLD)
        pause_window.bkgd(' ', curses.color_pair(4) | curses.A_BOLD)
        pause_window.border()
        pause_window.addstr(1, 3, ' GAME IS PAUSED')
        pause_window.addstr(2, 5, f' Points: {int(self.points)}')
        pause_window.refresh()
        pause_window.move(0, 0)
        key = -1
        while key != 32:
            key = self.screen.getch()

    def game_over(self):
        maxes = self.screen.getmaxyx()
        self.print_snake(False)
        score_window = curses.newwin(19, 40, 4, int(maxes[1] / 2) - 20)
        score_window.bkgdset(' ', curses.color_pair(4))
        score_window.bkgd(' ', curses.color_pair(4))
        score_window.border()
        midpoint = int(score_window.getmaxyx()[1] / 2)
        message4 = 'Press CTRL+C to exit'
        continue_message = 'Press any key to continue...'
        if self.lost:
            message1 = 'OH NOOES!!!!!!'
            message2 = f"Your snake died on level {self.level} "
            message25 = f"You had {int(self.points)} points"
            message3 = "Enter your initials: "
        else:
            message1 = 'Congratulations!!!!'
            message2 = f'Level {self.level} Complete'
            message25 = f'You have {int(self.points)} points'
            message3 = ''
            continue_message = f'Press any key to play level {self.level+1}'
        score_window.addstr(2, midpoint - int(len(message1) / 2), message1, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(4, midpoint - int(len(message2) / 2), message2, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(6, midpoint - int(len(message25) / 2), message25, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(14, midpoint - int(len(message4) / 2), message4, curses.color_pair(4) | curses.A_BOLD)
        score_window.addstr(9, midpoint - int(len(continue_message) / 2), continue_message, curses.color_pair(4))
        score_window.refresh()
        # make sure no stray keys are picked up
        clear_pause(score_window)

        if self.lost:
            message5 = "HIGH SCORES"
            score_window.clear()
            self.high_scores = self.get_scores()
            sorted_scores = sorted(self.high_scores, key=lambda item: int(item['score']), reverse=True)
            score_list_length = len(sorted_scores)
            if score_list_length > 10:
                score_list_length = 9
            else:
                score_list_length = score_list_length-1
            if int(self.points) > int(sorted_scores[score_list_length][self.score_fields[1]]):
                # get real input
                curses.echo()
                curses.nocbreak()
                score_window.clear()
                curses.curs_set(1)
                score_window.addstr(2, midpoint - int(len(message5) / 2), message5, curses.color_pair(4) | curses.A_BOLD)
                score_window.addstr(6, midpoint - int(len(message3) / 2)-4, message3, curses.color_pair(4))
                score_window.refresh()
                initials = score_window.getstr(3)
                curses.noecho()
                curses.cbreak()
                curses.curs_set(0)
                score_window.clear()
                self.add_score(initials, int(self.points), self.level)
                self.high_scores = self.get_scores()
            score_window.addstr(2, midpoint - int(len(message5) / 2), message5, curses.color_pair(4) | curses.A_BOLD)
            sorted_scores = sorted(self.high_scores, key=lambda item: int(item['score']), reverse=True)
            for i in range(10):
                if len(sorted_scores) > i:
                    score_line = f'{i+1} - {sorted_scores[i][self.score_fields[0]]}:' + \
                                 f' \t {sorted_scores[i][self.score_fields[1]]}' + \
                                 f'\t (Level {sorted_scores[i][self.score_fields[2]]})'
                    if i == 9:
                        score_window.addstr(4 + i, midpoint - 14-1, score_line, curses.color_pair(4))
                    else:
                        score_window.addstr(4+i, midpoint - 14, score_line, curses.color_pair(4))
            score_window.refresh()
            time.sleep(1)
            score_window.addstr(15, midpoint - int(len(continue_message) / 2), continue_message,
                                curses.color_pair(4))
            score_window.addstr(17, midpoint - int(len(message4) / 2), message4, curses.color_pair(4) | curses.A_BOLD)
            score_window.refresh()
            clear_pause(score_window)

        if self.lost:
            return self.lost, self.points, self.walls, self.speed, self.level, self.level_up
        else:
            return self.lost, self.points + self.snake.l, self.walls + 5, self.start_speed * .95, self.level +1, self.level_up

    def print_snake(self, check_dead=True):
        maxes = self.screen.getmaxyx()
        self.screen.clear()
        self.screen.border()
        if self.display_scores:
            interval = int(maxes[1] / 4)
            if interval < 12:
                p_string = "P: "
                w_string = "W: "
                s_string = "S: "
                l_string = "L: "
            else:
                p_string = "Points: "
                w_string = "Walls: "
                s_string = "Speed: "
                l_string = "Level: "
            self.screen.addstr(0, 2, l_string + str(int(self.level)))
            self.screen.addstr(0, 2 + interval, p_string + str(int(self.points)) + ' of ' + str(int(self.start_points + self.level_up)))
            self.screen.addstr(0, 2 + (interval * 2), w_string + str(self.walls))
            self.screen.addstr(0, 2 + (interval * 3), s_string + str(round(self.speed, 2)))

        if len(self.snake.a) < self.min_apples:
            self.snake.apple(maxes)
        if self.snake.eat(self.growth):
            curses.beep()
            self.points = self.points + self.walls
        if self.snake.dead(maxes) and check_dead:
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
        self.screen.refresh()

    def check_size(self):
        wrong_size = True
        while wrong_size:
            maxes = self.screen.getmaxyx()
            if maxes[0] <= 25 or maxes[1] <= 40:
                self.screen.addstr(2, 2, f'Screen too small')
                self.screen.addstr(3, 2, f'({maxes[0]}, {maxes[1]} < 25, 40)' )
                self.screen.addstr(4, 2, 'Press a key to recalculate')
                self.screen.border()
                self.screen.refresh()
                clear_pause(self.screen)
                self.screen.clear()
            else:
                wrong_size = False

    def play(self):
        try:
            self.check_size()
            self.screen.nodelay(True)
            if self.level == 1:
                menu_finished = None
                while not menu_finished:
                    menu_finished = self.menu(menu_finished)
                self.speed, self.walls, self.level_up = menu_finished
                self.snake.h = self.walls
                self.start_speed = self.speed
            self.snake.wall(self.screen.getmaxyx())
            self.print_snake()
            self.countdown()
            while True:
                self.print_snake()
                if self.fast:
                    time.sleep(self.speed/4)
                    key = 999
                    last_key = -1
                    # TODO: Find way of making this faster
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
                    elif key == 118 or key == 86:
                        self.display_scores = not self.display_scores
                    else:
                        self.fast = False
                self.snake.move()
                if not self.fast:
                    self.ticks = self.ticks + 1
                if self.ticks % 103 == 0:
                    self.speed = self.speed * .95
                if self.ticks % 343 == 0:
                    self.growth = self.growth + 1
                if self.ticks % 198 == 0:
                    self.min_apples = self.min_apples + 1
                if self.points > self.start_points + self.level_up:
                    break
                self.points = self.points + (1 - self.speed)
        except SnakeDead:
            self.lost = True
        return self.game_over()

    def menu(self, second):
        maxes = self.screen.getmaxyx()
        self.screen.clear()
        quit_message = 'Press CTRL+C to exit'
        difficulties = ['Lily', 'Easy', 'Moderate', 'Hard', 'Impossible']
        time_walls = [(.5,1,300),(0.4, 5, 400),(0.2,10, 600),(0.15,15, 800),(0.1,20, 1000)]
        menu_window = curses.newwin(8+len(difficulties), 34, int(maxes[0]/2)-7, int(maxes[1] / 2) - 17)
        menu_window.bkgdset(' ', curses.color_pair(4) | curses.A_BOLD)
        menu_window.bkgd(' ', curses.color_pair(4) | curses.A_BOLD)
        menu_window.border()
        menu_window.refresh()
        midpoint = int(menu_window.getmaxyx()[1] / 2)
        menu_window.addstr(len(difficulties)+6, midpoint - int(len(quit_message) / 2),
                           quit_message, curses.color_pair(4))
        for i in range(len(difficulties)):
            menu_window.addstr(2+i, 7, str(i+1) + '. ' + difficulties[i], curses.color_pair(4) | curses.A_BOLD )
        if second is not None:
            menu_window.addstr(len(difficulties) + 3, 5, 'INVALID CHOICE!',
                               curses.color_pair(4) | curses.A_BOLD)

        menu_window.addstr(len(difficulties)+4, 4, 'Enter a Difficulty level: ', curses.color_pair(4) | curses.A_BOLD)
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        menu_window.refresh()
        choice = None
        try:
            input = menu_window.getstr(1).decode('ascii')
            choice = int(input)-1
        except ValueError:
            pass
        if choice not in range(len(difficulties)):
            if choice == 0:
                pass
            return False
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        menu_window.clear()
        return time_walls[int(choice)]


if __name__ == '__main__':
    initial_speed = 0.3
    initial_difficulty = 10
    initial_start_points = 0
    initial_start_level = 1
    initial_level_up = 400
    speed = initial_speed
    difficulty = initial_difficulty
    start_level = initial_start_level
    start_points = initial_start_points
    level_up = initial_level_up
    while True:
        game = SnakeGame(start_speed=speed,
                         walls=difficulty,
                         points=start_points,
                         level=start_level,
                         level_up=level_up)
        try:
            lost, new_start_points, new_walls, new_speed, new_start_level, new_level_up = game.play()
            if not lost:
                start_points = new_start_points
                difficulty = new_walls
                speed = new_speed
                start_level = new_start_level
                level_up = new_level_up
            else:
                speed = initial_speed
                difficulty = initial_difficulty
                start_level = initial_start_level
                start_points = initial_start_points
        except KeyboardInterrupt:
            curses.nocbreak()
            game.screen.keypad(False)
            curses.echo()
            curses.endwin()
            quit()
