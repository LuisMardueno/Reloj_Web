from machine import Pin, I2C, RTC
import utime, network, urequests
from oled import Write,SSD1306_I2C, GFX
from oled.fonts import ubuntu_15
from icons import *
##
scl = Pin(19)
sda = Pin(18)

i2c = I2C(1,scl=scl, sda=sda)
Pin(14, Pin.OUT, value=1)

oled = SSD1306_I2C(128, 64, i2c)
write15 = Write(oled, ubuntu_15)
gfx = GFX(128, 64, oled.pixel)

def cls():
    oled.fill(0)
    oled.show()
###


def cargaIcono(res,eje_x,eje_y):
    for y, row in enumerate(res):
        for x, c in enumerate(row):
            oled.pixel(x+eje_x,y+eje_y,c)

# user data

url = "http://worldtimeapi.org/api/timezone/America/Tijuana" # see http://worldtimeapi.org/timezones
web_query_delay = 60000 # interval time of web JSON query
retry_delay = 5000 # interval time of retry after a failed Web query

# initialization

# SSD1306 OLED display

oled.fill(0)
oled.text("Connecting", 0, 5)
oled.text(" to wifi...", 0, 15)
oled.show()

# internal real time clock
rtc = RTC()

# wifi connection
wifi = network.WLAN(network.STA_IF) # station mode
wifi.active(True)
wifi.connect("Totalplay-D9AA","D9AADA5AjTMef7cP", channel=7)

# wait for connection
while not wifi.isconnected():
    pass

# wifi connected
print("IP:", wifi.ifconfig()[0], "\n")
oled.text("Connected. IP: ", 0, 35)
oled.text(" " + str(wifi.ifconfig()[0]), 0, 45)
oled.show()

# set timer
update_time = utime.ticks_ms() - web_query_delay


oled.show()

while True:
    
    # if lose wifi connection, reboot ESP8266
    if not wifi.isconnected():
        machine.reset()
    
    # query and get web JSON every web_query_delay ms
    if utime.ticks_ms() - update_time >= web_query_delay:
    
        # HTTP GET data
        response = urequests.get(url)
    
        if response.status_code == 200: # query success
        
            print("JSON response:\n", response.text)
            
            # parse JSON
            parsed = response.json()
            datetime_str = str(parsed["datetime"])
            year = int(datetime_str[0:4])
            month = int(datetime_str[5:7])
            day = int(datetime_str[8:10])
            hour = int(datetime_str[11:13])
            minute = int(datetime_str[14:16])
            second = int(datetime_str[17:19])
            subsecond = int(round(int(datetime_str[20:26]) / 10000))
        
            # update internal RTC
            rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
            update_time = utime.ticks_ms()
            print("RTC updated\n")
   
        else: # query failed, retry retry_delay ms later
            update_time = utime.ticks_ms() - web_query_delay + retry_delay
    
    # generate formated date/time strings from internal RTC
    date_str = "fecha: {1:02d}/{2:02d}/{0:4d}".format(*rtc.datetime())
    time_str = "{4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())

    # update SSD1306 OLED display
    while  hour >= 8 and hour < 18:
        oled.fill(1)
        res = get_icon("Sun")
        cargaIcono(res,60,10)
        res = get_icon("Edificio1")
        cargaIcono(res,-5,28)
        write15.text(date_str, 0, 49,0,1)
        write15.text(time_str, 0, 0,0,1)
        gfx.line(0, 50, 127, 50, 0)
        oled.show()
        utime.sleep(0.1)
        break
    if hour >= 18:
        oled.fill(0)
        res = get_icon("Moon")
        cargaIcono(res,60,10)
        res = get_icon("Edificio0")
        cargaIcono(res,-5,28)
        write15.text(time_str, 0, 0)
        gfx.fill_rect(0, 50, 127, 50, 1)
        write15.text(date_str, 0, 50,0,1)
        oled.show()
        utime.sleep(0.1)
