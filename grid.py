import time
from ulab import numpy as np

class Grid:
    MAX_BRIGHTNESS = 64
    Y_INDEX = 0
    X_INDEX = 1
    B_INDEX = 2

    def __init__(self):
        # y position of the horizon
        self._horizon_y = 92

        # Setup brightness values to be assigned so that the horizontal
        # lines get brighter as they get closer
        self._z_fade = np.linspace(self.MAX_BRIGHTNESS, 0, self._horizon_y + 1, dtype=np.uint8)

        vertical_end = self._horizon_y - 3

        # Create the non-horizontal lines

        self._static_lines = bytearray()
        self._static_lines += self.line(0, 32, 100, vertical_end, self._z_fade[3], self._z_fade[self._horizon_y])
        self._static_lines += self.line(0, 66, 80, vertical_end, self._z_fade[66], self._z_fade[self._horizon_y])
        self._static_lines += self.line(64, 0, 120, vertical_end, self._z_fade[0], self._z_fade[self._horizon_y])
        self._static_lines += self.line(192, 0, 132, vertical_end, self._z_fade[0], self._z_fade[self._horizon_y])
        self._static_lines += self.line(255, 24, 152, vertical_end, self._z_fade[24], self._z_fade[self._horizon_y])
        self._static_lines += self.line(255, 66, 172, vertical_end, self._z_fade[66], self._z_fade[self._horizon_y])

        # Draw a frame around the edges
        self._static_lines += self.line(255,128,255,0,self.MAX_BRIGHTNESS, self.MAX_BRIGHTNESS)
        self._static_lines += self.line(255,0,0,0,self.MAX_BRIGHTNESS, self.MAX_BRIGHTNESS)
        self._static_lines += self.line(0,0,0,255,self.MAX_BRIGHTNESS, self.MAX_BRIGHTNESS)
        self._static_lines += self.line(0,255,255,255,self.MAX_BRIGHTNESS, self.MAX_BRIGHTNESS)
        self._static_lines += self.line(255,255,255,129,self.MAX_BRIGHTNESS, self.MAX_BRIGHTNESS)

        # z positions for the horizontal grid lines
        self._z_positions = np.array([1.0, 2.1, 3.2, 4.3, 5.4])
        self._h_lines = []

        # Initialize horizontal lines
        for z_index in range(0, len(self._z_positions)):
            # Convert z position to y
            yp = int(self._horizon_y - 2**self._z_positions[z_index])

            # Get the brightness based on the z position
            yb = self._z_fade[yp]

            # Draw back and forth to reduce the beam travel between lines
            if z_index % 2 == 0:
                # Create the line
                self._h_lines.append(np.array(self.line(0, yp, 255, yp, yb, yb), dtype=np.uint8))
            else:
                # Create the line
                self._h_lines.append(np.array(self.line(255, yp, 0, yp, yb, yb), dtype=np.uint8))

        self._frame_time = time.monotonic()


    def line(self, x1, y1, x2, y2, b1, b2):
        # Determine the number of points needed for the line
        num_points = max(abs(x2 - x1), abs(y2 - y1)) + 1

        yp = np.linspace(y1, y2, num_points, dtype=np.uint8)
        xp = np.linspace(x1, x2, num_points, dtype=np.uint8)
        bp = np.linspace(b1, b2, num_points, dtype=np.uint8)

        # Create a results array large enough for four bytes per point
        results = np.zeros(num_points * 4, dtype=np.uint8)

        # Copy values into results
        results[self.X_INDEX::4] = xp[::]
        results[self.Y_INDEX::4] = yp[::]
        results[self.B_INDEX::4] = bp[::]

        return results.tobytes()


    def draw_grid(self, draw_buffer, index):
        data_buff = bytearray()

        # Move horizontal lines along z axis based on elapsed time since previous frame
        self._z_positions += time.monotonic() - self._frame_time
        self._frame_time = time.monotonic()
        # Wrap around to start a new line when a line reaches the bottom of the screen
        self._z_positions = self._z_positions - np.where(self._z_positions > 6.50, 5.50, 0)

        # Update horizontal lines
        for zi in range(len(self._z_positions)):
            # Convert z value to y position
            yp = int(self._horizon_y - 2**self._z_positions[zi])
            # Set the lines y value
            self._h_lines[zi][self.Y_INDEX::4] = yp
            # Set the lines brightness
            self._h_lines[zi][self.B_INDEX::4] = self._z_fade[yp]
            # Add the line to the data
            data_buff += self._h_lines[zi].tobytes()

        # Add static lines to the data
        data_buff += self._static_lines

        byte_count = len(data_buff)
        draw_buffer[index:(index + byte_count)] = data_buff

        return byte_count
