import numpy as np
import RPi.GPIO as GPIO
import spidev, time

'''Intializing Pi and input channels'''
GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22],GPIO.OUT, initial = 0) #Output channels to control stepper motor
GPIO.setup([25,24], GPIO.IN) #two input channels for on/off and CW/CCW
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

'''
these will be an input from switch boards, was intially testing
on/off and CW/CCW functionality with explicit variables, then
switched to being controlled with GPIO inputs
'''
#on_off = GIPO.input(25)
#on_off = 1 #0 off, 1 on
#cw_ccw = 0 #0 cw, 1 ccw
#speed = 0.5 #float between 0.5-1, taken using voltage divider and a2d converter, 1 is slow, .5 is fast
#logic for stepper motor
#wait = 0.03 * speed

halfsteparr = [(1,0,0,1),(1,0,1,1),(1,0,1,0),(1,1,1,0),(0,1,1,0),(0,1,1,1),(0,1,0,1),(1,1,0,1)]
#used for delayed start, can be removed when using with final setup
input('Enter to start')

try:
  while 1:
    on_off = GPIO.input(25) #checking state of on off switch
    cw_ccw = GPIO.input(24) #checking state of cw ccw switch
    speed = (v_out()[1]*0.5)+0.05
    wait = 0.09 * speed
    if on_off:
        for logic in halfsteparr[::1]:#stepping through index every 1
          if cw_ccw ==1: #setting A1, A2, B1, & B2 to ensure correct rotation direction
            A1,A2,B1,B2 = [4,17,27,22] 
          elif cw_ccw == 0:#same as above but swap A1 & B1, and A2 & B2
            A1,A2,B1,B2 = [27,22,4,17]

          GPIO.output([A1,A2,B1,B2],logic)
          #print(log) #debug
          time.sleep(wait) #time to wait between stepping in motor
          #print(GPIO.input(25))
    else:
      time.sleep(0.005) #have the program wait a short time then check to see if the on/off switch has been flipped
except KeyboardInterrupt:
  pass
GPIO.cleanup()


