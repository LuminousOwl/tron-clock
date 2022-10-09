import board
import countio
from digitalio import Pull
import rtc
import time

# Handles buttons presses to adjust hours and minutes
class TimeButtons:
    def __init__(self):
        # Setup for buttons to adjust hours and minutes
        self._btn_hr_count = countio.Counter(board.GP17, edge=countio.Edge.RISE, pull=Pull.DOWN)
        self._btn_min_count = countio.Counter(board.GP19, edge=countio.Edge.RISE, pull=Pull.DOWN)
        self._button_time = None
        self._rtc = rtc.RTC()

    def handle_buttons(self):
        # Handle button presses to increment hours/minutes
        if self._button_time == None or ((time.monotonic() - self._button_time) > 0.3):
            # Increment the hour if button pressed
            if self._btn_hr_count.count > 0:
                rt = time.time()
                rt += 3600
                self._rtc.datetime = time.localtime(rt)
                self._button_time = time.monotonic()
                self._btn_hr_count.reset()

            # Increment the minute if button pressed
            if self._btn_min_count.count > 0:
                rt = time.time()
                rt += 60
                self._rtc.datetime = time.localtime(rt)
                self._button_time = time.monotonic()
                self._btn_min_count.reset()
        else:
            # Reset for debounce
            self._btn_hr_count.reset()
            self._btn_min_count.reset()
