import os
import wifi
import socketpool
import adafruit_ntp
import rtc

class TimeWIFI:
    def sync_time():
        wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=-4)
        r = rtc.RTC()
        r.datetime = ntp.datetime
