import time
from squid import *
from subprocess import call
from datetime import datetime
import sys
import signal

#import evdev
from evdev import InputDevice, categorize, ecodes

def shootPhoto(mode):
    global ready_color
    rgb.set_color(RED)
    i = datetime.now()               #take time and date for filename  
    now = i.strftime('%Y%m%d-%H%M%S')  
    photo_name = now
    
    #reset select count for wifi
    global select_counter
    select_counter = 0
    
    #print("shooting photo - camera mode")
    #print(mode)
    
    if mode == 0:
        #do a regular photo
        #call command line raspistill -t = 1 second; -tl = timelapse as fast as possible; -bm = burst mode; -o = output save as
        cmd = 'raspistill -t 1000 -tl 0 -n -ex auto -awb incandescent -bm  -o /home/pi/Pictures/' + photo_name + '-seq%02d.jpg'   
    elif mode == 1:
        #do a timelapse
        rgb.set_color(PURPLE)
        time.sleep(5)
        rgb.set_color(RED)
        cmd = 'raspistill -t 20000 -tl 1000 -n -ex auto -awb incandescent -o /home/pi/Pictures/' + photo_name + '-timelapse%04d.jpg'
    elif mode == 2:
        #night mode
        cmd = 'raspistill -t 1000 -tl 0 -n -ex night -awb incandescent -bm -o /home/pi/Pictures/' + photo_name + '-night%02d.jpg'
    elif mode == 3:
        #do a regular photo
        #call command line raspistill -t = 1 second; -tl = timelapse as fast as possible; -bm = burst mode; -o = output save as
        cmd = 'raspistill -t 1000 -tl 0 -n -ex spotlight -awb incandescent -bm  -o /home/pi/Pictures/' + photo_name + '-spot%02d.jpg' 
    
    call ([cmd], shell=True)         #shoot the photo
    rgb.set_color(ready_color)

def toggle_wifi():
    global wifi
    global select_counter
    select_counter = 0
    if wifi:
        cmd = 'sudo rfkill unblock wifi'
        call ([cmd], shell=True) 
        cmd = 'sudo ifconfig wlan0 down'
        call ([cmd], shell=True)  
        wifi = False
        rgb.set_color(RED)
        time.sleep(.5)
        rgb.set_color(BLUE)
        time.sleep(.5)
        rgb.set_color(RED)
        time.sleep(.5)
        rgb.set_color(BLUE)
        time.sleep(.5)
        rgb.set_color(RED)
        time.sleep(.5)
        rgb.set_color(BLUE)
        time.sleep(1)
        rgb.set_color(ready_color)
        
    else:
        cmd = 'sudo rfkill unblock wifi'
        call ([cmd], shell=True)
        cmd = 'sudo ifconfig wlan0 up'
        call ([cmd], shell=True)  
        wifi = True
        rgb.set_color(BLUE)
        time.sleep(.5)
        rgb.set_color(RED)
        time.sleep(.5)
        rgb.set_color(BLUE)
        time.sleep(.5)
        rgb.set_color(RED)
        time.sleep(.5)
        rgb.set_color(BLUE)
        time.sleep(.5)
        rgb.set_color(RED)
        time.sleep(1)
        rgb.set_color(ready_color)

    
def get_location():
    #print("except")
    rgb.set_color(CYAN)
    global devicelocation
    global counter
    
    if counter == 0:
        devicelocation = '/dev/input/event1'
        counter=counter+1;
    elif counter == 1:
        devicelocation = '/dev/input/event2'
        counter=counter+1;
    elif counter == 2:
        devicelocation = '/dev/input/event3'
        counter=counter+1;
    elif counter == 3:
        devicelocation = '/dev/input/event4'
        counter=counter+1;
    else:
        devicelocation = '/dev/input/event0'
        counter = 0
        time.sleep(5)

                
#loop and filter by event code and print the mapped label
def process_events():
    global devicelocation
    global select_counter
    
    #print(devicelocation)
    
    try:
        
        #find_gamepad()
        #gamepad0 = InputDevice('/dev/input/event0')
        #gamepad1 = InputDevice('/dev/input/event1')
        #gamepad2 = InputDevice('/dev/input/event2')
        #gamepad3 = InputDevice('/dev/input/event3')
        
        gamepad = InputDevice(devicelocation)
        #print(gamepad.name)
        #print("gamepad name \n")
        #print(devicelocation)
        
        if gamepad.name == "8BitDo N30 Pro 2":
            gamepad.grab()
            
            rgb.set_color(ready_color)
        
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_KEY:
                    if event.value == 1:
                        #print(event.code)
                        if event.code == aBtn:
                            shootPhoto(auto_mode)
                        elif event.code == bBtn:
                            shootPhoto(night_mode)
                        elif event.code == yBtn:
                            shootPhoto(timelapse_mode)
                        elif event.code == xBtn:
                            shootPhoto(spotlight_mode)
                        elif event.code == select:
                            rgb.set_color(WHITE)
                            time.sleep(.2)
                            rgb.set_color(GREEN)
                            print(select_counter)
                            if select_counter >= 5:
                                toggle_wifi()
                            else:
                                select_counter = select_counter+1
                        else:
                            select_counter = 0
        else:
            get_location()
        
    except:
        get_location()
        return False


#init remote
#gamepad = InputDevice('/dev/input/event0')
#init camera mode AUTO
auto_mode = 0
night_mode = 2
timelapse_mode = 1
spotlight_mode = 3
#AUTO == green
ready_color = GREEN


devicelocation = '/dev/input/event1'
counter = 1
select_counter = 0
wifi = True


#init LED and set to ready_color
rgb = Squid(4, 17, 27)
rgb.set_color(ready_color)
#write a set color function so i can turn off the led if I want

#button code variables for 8bitdo n30 pro 2

#shutter auto 
aBtn = 304

#shutter night
bBtn = 305

#something btn
xBtn = 307

#shutter timelapse 20s 1s intervals
yBtn = 308

start = 315
select = 314

l1 = 310
l2 = 312
r1 = 311
r2 = 313

while True:
    process_events()

