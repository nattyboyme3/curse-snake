# Curse Snake 
## (Python Snake game using curses library)

 - Requires Python 3.6+

To run: 

```python3 snake.py```

Available arguments: 

```python3 snake.py [infinite] [<move interval>] [<number of walls>]```

Turning the infinite option on provides an extra challenge: the game doesn't erase snake body characters after the snake has left the space. You can still reuse these spaces, but you might run into your tail once it gets long.

The move interval is in units of seconds. A recommended starting interval is .3 seconds, or .15 seconds if you don't have walls. 

The number of walls created increases the difficulty. 0 to 20 walls is a good starting place. 
