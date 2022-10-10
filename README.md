# tron-clock
#TRON Oscilloscope Clock

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/OOFGKmF-wbw/0.jpg)](https://www.youtube.com/watch?v=OOFGKmF-wbw)


## About
The source code is for CircuitPython to run on the Raspberry Pi Pico or Pi Pico W. There is code to initialize the time over WIFI or adjust the hours and minutes using buttons. Either can be disabled relatively easily by removing or commenting imports and code out in the tron.py file. WIFI requires CircuitPython 8.0.0-beta.1 or later. The code requires an AD7302 DAC, but could use an R-2R or other type of DAC by replacing the ad7302.py file.

PIO is used to output data in parallel to the AD7302. Each 32 bits of data contains 8-bit x and y values and an 8-bit relative brightness. Frame rates tend to be around 80-90fps, but fall as low as 20fps during the zoom transition animation. A looping background write is used to allow the screen to refresh at a high rate regardless of the frame rate. Data is stored in ulap.numpy arrays to allow quick updates for the animations.



## Wiring
```
Pico  AD7302
 GP0   DB0
 GP1   DB1
 GP2   DB2
 GP3   DB3
 GP4   DB4
 GP5   DB5
 GP6   DB6
 GP7   DB7
 GP8   !WR
 GP9   A/B
GP10   !LDAC
VSYS   !PD
VSYS   !CLR
VSYS   REFIN
VSYS   VDD
 GND   !CS
 GND   AGND
 GND   DGND
```
