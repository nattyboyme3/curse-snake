# Curse Snake 
 Python Snake game using Python curses library

**Requires [Python 3.6+](https://www.python.org/downloads/) and works on MacOS**

(looking for Windows NCurses developers to contribute to Windows compatibility)

To play: 

- Run ```python3 snake.py``` from a ```curses```-compatible terminal (Terminal.app, for instance)
 
To clear high scores:
 
- Delete ```.snake_scores.csv``` in the working directory

To Cheat: 
- Edit in a ridiculously high score into ```.snake_scores.csv``` in the format ```[initials],[score],[level]```
 
## Gameplay

This is a classic snake game in the style of the games I remember from the days of Nokia brick phones. The goal of the game is to eat apples while avoiding walls, obstacles and the snake's own body. 

Each apple increases the length of the snake, and over time the snake begins to move faster.

Points are awarded for each snake movement, with a larger number of additional points awarded for eating apples.

## Difficulty

- **Lily**: Named for my youngest daughter, appropriate for a 4-year-old skill level. *(1 Wall to start, 0.5 second movement intervals, levels up after 300 points)*
- **Easy**: A nice easy snake game. *(5 walls to start, 0.4 seconds per move, levels up after 400 points)*
- **Moderate:** Medium difficulty for medium people with moderate personalities. *(10 walls, 0.2 seconds per move, levels up after 600 points)*
- **Hard:** A substantial challenge for the average player. *(15 walls, 0.15 seconds per move, levels up after 800 points)*
- **Impossible:** Still challenging to the author. *(20 walls, 0.1 seconds per move, levels up after 1000 points)*


## Controls
| Function | Key(s)|
| --- | --- |
| **Movement** | <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd>, or <kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|
| **Pause** | <kbd>Space</kbd> |
| **Hide Points Display** | <kbd>V</kbd> |
| **Exit** | <kbd>Ctrl</kbd>+<kbd>C</kbd> |
