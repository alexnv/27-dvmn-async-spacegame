import asyncio
import time
import curses
from random import randint, choice

from curses_tools import read_frames, read_controls, draw_frame

FRAMES = read_frames()


async def animate_spaceship(canvas, start_row, start_column, speed=1):
    canvas.nodelay(True)
    max_row, max_column = canvas.getmaxyx()
    while True:
        rows_direction, columns_direction, _ = read_controls(canvas)
        start_row += rows_direction*speed
        start_column += columns_direction*speed
        frame = next(FRAMES)
        if start_row < 1:
            start_row = 1
        if start_column < 1:
            start_column = 1
        if start_column > max_column - 6:
            start_column = max_column - 6
        if start_row > max_row - 10:
            start_row = max_row - 10
        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)
        canvas.border()


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(randint(0, 2000)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(randint(0, 300)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(randint(0, 500)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(randint(0, 300)):
            await asyncio.sleep(0)


def draw(canvas):
    x_max, y_max = canvas.getmaxyx()
    x_max -= 2
    y_max -= 2
    coroutines = [blink(canvas, randint(1, x_max), randint(1, y_max), choice('+*.:')) for _ in range(randint(0, 300))]
    coroutines.extend([fire(canvas, x_max / 2, y_max / 2, rows_speed=-0.03, columns_speed=0),
                       animate_spaceship(canvas, x_max / 2, y_max / 2, 2)])
    while True:
        canvas.border()
        curses.curs_set(False)
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        time.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
