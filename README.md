# tron-clock
TRON Oscilloscope Clock

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/OOFGKmF-wbw/0.jpg)](https://www.youtube.com/watch?v=OOFGKmF-wbw)

The source code is for CircuitPython to run on the Raspberry Pi Pico or Pi Pico W. There is code to initialize the time over WIFI or adjust the hours and minutes using buttons. Either can be disabled relatively easily by removing or commenting imports and code out in the tron.py file. WIFI requires CircuitPython 8.0.0-beta.1 or later. The code requires an AD7302 DAC, but could use an R-2R or other type of DAC by replacing the ad7302.py file.

PIO is used to output data in parallel to the AD7302. Each 32 bits of data contains 8-bit x and y values and an 8-bit relative brightness. Frame rates tend to be around 80-90fps, falling as low as the 20fps during the zoom transition animation. A looping background write is used to allow the screen to refresh at a high constant rate even as the frame rates drop. 
