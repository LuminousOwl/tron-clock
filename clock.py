import binascii
import time
import math
from ulab import numpy as np

class Clock:
    X_INDEX = 1
    Y_INDEX = 0
    B_INDEX = 2

    TRANSITION_NONE = 0
    TRANSITION_OUT = 1
    TRANSITION_IN = 2

    Y_POSITION = 140
    MAX_BRIGHTNESS = 32

    def __init__(self):
        self._transition_phase = self.TRANSITION_NONE
        self._transition_out = None
        self._transition_in = None
        self._transition_started = 0

        self._time_data = None
        self._display_minutes = None
        self._display_hours = None

        local_time = time.localtime()
        self._minutes = local_time.tm_min

        self._last_percent = 0

        self._load_char_data()

        self._time_str = "     "
        self._load_time(local_time.tm_hour, self._minutes)


    # Load x/y character data from base64 text in char_data.txt
    def _load_char_data(self):
        self._char_data = {}

        # Chars to have data read from file
        chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":"]
        char_index = 0

        # Open the file and read each line as base64 data for a character
        with open('char_data.txt') as f:
            for line in f:
                self._char_data[chars[char_index]] = binascii.a2b_base64(line)
                char_index += 1


    # Returns character data with x/y offsets and a specified brightness
    def _get_char(self, char, x_offset, y_offset=Y_POSITION, brightness=MAX_BRIGHTNESS):
        paths = np.array(self._char_data[char])
        out_data = np.zeros(len(paths) * 2, dtype=np.uint8)
        out_data[self.Y_INDEX::4] = paths[1::2] + y_offset
        out_data[self.X_INDEX::4] = paths[0::2] + x_offset
        out_data[self.B_INDEX::4] = brightness

        return out_data

    # Get an array of x positions to use for the time characters
    def _get_char_positions(self, time_str):
        positions = [20, 68, 120, 144, 192]

        # The 1 character gets special treatment since is it not as wide
        for char_index in range(0, 5):
            if char_index == 0 and time_str[0] == "1":
                positions[0] += 8

            if time_str[char_index] == "1":
                positions[char_index] += 8

        return positions

    # Create a time string for hours/minutes
    def _time_as_str(self, hour, minutes):
        hour_str = str(hour)

        if len(hour_str) == 1:
            hour_str = "0" + hour_str

        minute_str = str(minutes)

        if len(minute_str) == 1:
            minute_str = "0" + minute_str

        return hour_str + ":" + minute_str

    # Load data for the given time
    def _load_time(self, hour, minutes):
        self._prev_time_str = self._time_str

        # Create a string for the time
        self._time_str = self._time_as_str(hour, minutes)

        # Get the x positions for each time character
        x_positions = self._get_char_positions(self._time_str)

        self._time_data = [ ]

        # Get data for each character with offsets
        self._time_data.append(np.array(self._get_char(self._time_str[0], x_positions[0]), dtype=np.uint8))
        self._time_data.append(np.array(self._get_char(self._time_str[1], x_positions[1]), dtype=np.uint8))
        self._time_data.append(np.array(self._get_char(self._time_str[2], x_positions[2], self.Y_POSITION + 4), dtype=np.uint8))
        self._time_data.append(np.array(self._get_char(self._time_str[3], x_positions[3]), dtype=np.uint8))
        self._time_data.append(np.array(self._get_char(self._time_str[4], x_positions[4]), dtype=np.uint8))

    # Calculate percentage of transition
    def _transition_percent(self, transition_secs):
        if self._last_percent == 1:
            self._last_percent = 0
            return None

        draw_percent = (time.monotonic() - self._transition_started) / transition_secs
        draw_percent = min(1, draw_percent)

        self._last_percent = draw_percent

        return self._last_percent


    def _transition_trail(self):
        if self._transition_phase == self.TRANSITION_OUT:
            draw_percent = self._transition_percent(0.5)
        else:
            draw_percent = self._transition_percent(1.5)

        if draw_percent == None:
            return None

        if self._transition_phase == self.TRANSITION_OUT:
            draw_percent = 1.0 - draw_percent

        data_buff = bytearray()

        for char_index in range(0, 5):
            draw_len = int(len(self._time_data[char_index]) / 4 * draw_percent) * 4

            if self._transition_phase == self.TRANSITION_OUT:
                draw_start = len(self._time_data[char_index]) - draw_len
                data_buff += self._time_data[char_index][draw_start:]
            else:
                path_buff = self._time_data[char_index][:draw_len].copy()
                bright_start = max(len(path_buff) - 64, 0)
                path_buff[bright_start + self.B_INDEX::4] = 255

                data_buff += path_buff

        return data_buff

    def _transition_zoom(self):
        draw_percent = self._transition_percent(1.5)

        if draw_percent == None:
            return None

        if self._transition_phase == self.TRANSITION_OUT:
            draw_percent = 1.0 - draw_percent

        out_bytes = bytearray()

        for char_index in range(0, 5):
            data_buff = np.array(self._time_data[4 - char_index], dtype=np.float)
            scale = 2**(6.64385 * draw_percent) / 100.0
            data_buff[self.X_INDEX::4] -= 128
            data_buff[self.Y_INDEX::4] -= self.Y_POSITION
            data_buff *= scale
            data_buff[self.Y_INDEX::4] -= 46 * (1 -  scale)
            data_buff[self.Y_INDEX::4] += self.Y_POSITION
            data_buff[self.X_INDEX::4] += 128
            data_buff = np.array(data_buff, dtype=np.uint8)
            out_bytes += data_buff.tobytes()

        return out_bytes

    def _transition_fade(self):
        draw_percent = self._transition_percent(1)

        if draw_percent == None:
            return None

        out_bytes = bytearray()
        if draw_percent > 0.5:
            return out_bytes

        for char_index in range(0, 5):
            data_buff = np.array(self._time_data[4 - char_index], dtype=np.float)
            data_buff[self.B_INDEX::4] *= 1 - draw_percent * 2
            data_buff = np.array(data_buff, dtype=np.uint8)
            out_bytes += data_buff.tobytes()

        return out_bytes

    def draw_time(self, buffer, index):
        local_time = time.localtime()
        minutes = local_time.tm_min
        hours = local_time.tm_hour
        draw_data = None

        # If we are in a transition animation
        if self._transition_phase != self.TRANSITION_NONE:
            # Draw the next value
            if self._transition_phase == self.TRANSITION_IN:
                draw_data = self._transition_in()
            else:
                draw_data = self._transition_out()


            # If no data was returned the transition is done
            if draw_data is None:
                # If the transtion was an out transition, switch to the in transition
                if self._transition_phase == self.TRANSITION_OUT:
                    self._transition_phase = self.TRANSITION_IN
                    self._load_time(local_time.tm_hour, minutes)
                    self._transition_started = time.monotonic()
                    draw_data = self._transition_in()

                # If the transition was an in transition we are done transitioning
                elif self._transition_phase == self.TRANSITION_IN:
                    self._transition_phase = self.TRANSITION_NONE
        elif minutes != self._display_minutes or hours != self._display_hours:
            # Minutes have changed start transitioning out
            self._transition_phase = self.TRANSITION_OUT
            if hours != self._display_hours:
                self._transition_out = self._transition_trail
                self._transition_in = self._transition_zoom
            else:
                self._transition_out = self._transition_fade
                self._transition_in = self._transition_trail

            self._transition_started = time.monotonic()
            self._next_time_str = self._time_as_str(local_time.tm_hour, minutes)
            self._display_minutes = minutes
            self._display_hours = hours
            # Draw the transition
            draw_data = self._transition_out()

        # If no transition data then just use the regular time data
        if draw_data == None:
            draw_data = np.concatenate((
            self._time_data[4],
            self._time_data[3],
            self._time_data[2],
            self._time_data[1],
            self._time_data[0]
            )).tobytes()

        # Get length and copy into the buffer
        data_length = len(draw_data)
        buffer[index:data_length] = draw_data

        # Return the length in bytes
        return data_length
