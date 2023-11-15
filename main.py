import asyncio
import time
import curses
from itertools import cycle
from random import randint, choice

from curses_tools import read_frames, read_controls, draw_frame, get_frame_size


async def animate_spaceship(canvas, start_row, start_column, spaceship_frames):
    border_size = 1
    height, width = canvas.getmaxyx()
    height, width = height - border_size, width - border_size

    frame_rows, frame_columns = get_frame_size(spaceship_frames[0])
    height -= frame_rows
    width -= frame_columns

    for frame in cycle(spaceship_frames):
        for _ in range(2):
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)

            draw_frame(canvas, start_row, start_column, frame, negative=True)

            rows_direction, columns_direction, _ = read_controls(canvas)

            if rows_direction or columns_direction:
                start_row += rows_direction
                start_column += columns_direction

                start_row = max(1, start_row)
                start_column = max(1, start_column)

                start_row = min(start_row, height)
                start_column = min(start_column, width)


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


async def blink(canvas, row, column, symbol='*', offset_ticks=0):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(randint(0, offset_ticks)):
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
    spaceship_frames = read_frames()
    coroutines = [blink(
        canvas,
        randint(1, x_max),
        randint(1, y_max),
        choice('+*.:'),
        randint(1, 20)
    ) for _ in range(randint(0, 300))]
    coroutines.extend([fire(canvas, x_max / 2, y_max / 2, rows_speed=-0.03, columns_speed=0),
                       animate_spaceship(canvas, x_max / 2, y_max / 2, spaceship_frames)])
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

        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
