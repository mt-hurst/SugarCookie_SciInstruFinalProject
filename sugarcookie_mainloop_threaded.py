import threading
import numpy as np
import RPi.GPIO as GPIO
import spidev
import time

'''Intializing Pi and input channels'''
GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22,6,19,20],GPIO.OUT, initial = 0) #Output channels to control stepper motor
GPIO.setup([25,24,5], GPIO.IN) #two input channels for on/off and CW/CCW
'''setting up PWM for LED arrays'''
p1 = GPIO.PWM(6,60)
p2 = GPIO.PWM(19,60)

p1.start(0)
p2.start(0) #starting both LED arrays with 0 dc, thus appearing off

'''Analog to digital reading setup, written by Ran'''
spi = spidev.SpiDev() #open spi bus
spi.open(0,0) #open(bus, device)
spi.max_speed_hz=1000000
spi.mode = 0b00 #spi modes; 00,01,10,11

def read_adc(channel):
    if not 0 <= channel <= 7:
        raise IndexError('Invalid. enter 0, 1, ..., 7' )
    """datasheep page 19 about setting sgl/diff bit to high, hence we add 8 = 0b1000
    left shift 4 bits to make space for the second byte of data[1]"""
    request = [0x1, (8+channel) << 4, 0x0] # [start bit, configuration, listen space] 
    data = spi.xfer2(request) #data is recorded 3 bytes: data[0] - throw away, data[1] - keep last 2 bits, data[2] - keep all
    data10bit = ((data[1] & 3) << 8) + data[2] #shfit bits to get the 10 bit data
    return data10bit
'''end Prof Yang's Code'''
'''below this written by Tristan 11/4/21 '''
v_ref = 3.3
def v_out(chan = 0):
  doc = read_adc(chan) #binary # corresponding to analog input
  v_ana = doc*v_ref/1024 #this converts the binary # into a voltage
  frac = doc/1024
  return v_ana,frac

#input('Press Enter to Continue') #can remove for final design

###
'''Looping Functions'''
###
#stepper motor loop logic
halfsteparr = [(1,0,0,1),(1,0,1,1),(1,0,1,0),(1,1,1,0),(0,1,1,0),(0,1,1,1),(0,1,0,1),(1,1,0,1)]
def motor_loop(): #stepper motor loop control
    try:
        while 1:
            ONOFF = GPIO.input(25)
            rotation = GPIO.input(24)
            wait = (((v_out()[1]*0.6)+0.15)*0.09) #stepper motor wait time
            if ONOFF:
                GPIO.output(20,1) #send high signal to sleep to turn on motor
                for logic in halfsteparr[::1]:#stepping through index every 1
                      if rotation ==1: #setting A1, A2, B1, & B2 to ensure correct rotation direction
                        A1,A2,B1,B2 = [4,17,27,22] 
                      elif rotation == 0:#same as above but swap A1 & B1, and A2 & B2
                        A1,A2,B1,B2 = [27,22,4,17]
                      GPIO.output([A1,A2,B1,B2],logic)
                      time.sleep(wait)#time to wait between stepping in motor
            else:
                GPIO.output(20,0) #send high signal to sleep to turn on motor
                time.sleep(0.01)#waiting a short time then check if ONOFF switch flipped
    except KeyboardInterrupt:
      GPIO.cleanup()
      pass
#led loop PWM logic
pw1and2 = [range(10,101,2),range(100,9,-2)]
def led_loop(): #led motor loop control
    try:
        while 1:
            ONOFF = GPIO.input(25)
            #simulating high and low with code as switch being used
            #led_control = 1
            led_control = GPIO.input(5)
            wait = ((v_out()[1])*0.06+0.005)
            if led_control and ONOFF:
                ONOFF = GPIO.input(25)
                for i in range(0,45):
                  p1.ChangeDutyCycle(pw1and2[0][i])
                  p2.ChangeDutyCycle(pw1and2[1][i])
                  time.sleep(wait)
                for i in range(45,0,-1):
                  p1.ChangeDutyCycle(pw1and2[0][i])
                  p2.ChangeDutyCycle(pw1and2[1][i])
                  time.sleep(wait)
            else:
                p1.ChangeDutyCycle(0)
                p2.ChangeDutyCycle(0)
                time.sleep(0.01)
    except KeyboardInterrupt:
      GPIO.cleanup()  
      pass

#Threading Loops together so they run in parallel.

motor = threading.Thread(target = motor_loop)
led = threading.Thread(target = led_loop)

motor.start()
led.start()

try:
    while 1:
        motor.join()
        led.join()
except KeyboardInterrupt:
    GPIO.cleanup()
    pass
GPIO.cleanup



