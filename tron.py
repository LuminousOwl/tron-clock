import time
from grid import Grid
from clock import Clock
from time_wifi import TimeWIFI
from time_buttons import TimeButtons
from ad7302 import AD7302

clock = Clock()
grid = Grid()
dac = AD7302()
time_buttons = TimeButtons()

# Initialize the time
TimeWIFI.sync_time()

draw_buff = bytearray(17000)

while True:
    # Get the data to draw
    byte_count = 0
    byte_count += clock.draw_time(draw_buff, byte_count)
    byte_count += grid.draw_grid(draw_buff, byte_count)

    # Write to the DAC
    dac.write(draw_buff, byte_count)

    # Handle button presses
    time_buttons.handle_buttons()

