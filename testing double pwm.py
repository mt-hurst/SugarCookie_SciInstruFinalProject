

import time
import RPi.GPIO as GPIO
import math

pw1and2 = [range(10,101),range(100,9,-1)]
#above line creates a list of duty cycles to iterate over in a for loop
#the first element is the range of duty cycles for PWM1
#the second element is the range of duty cyles for PWM2

GPIO.setmode(GPIO.BCM)

GPIO.setup([18,22,23], GPIO.OUT)
GPIO.output([18,22,23],0)
p1 = GPIO.PWM(18,60)
p2 = GPIO.PWM(22,60)
waittime = 0.02 #can use this variable to control the speed of the flickering
p1.start(0)
p2.start(0)
try:
    while True:
        for i in range(0,90):
          p1.ChangeDutyCycle(pw1and2[0][i])
          p2.ChangeDutyCycle(pw1and2[1][i])
          time.sleep(waittime)
        for i in range(90,0,-1):
          p1.ChangeDutyCycle(pw1and2[0][i])
          p2.ChangeDutyCycle(pw1and2[1][i])
          time.sleep(waittime)
except KeyboardInterrupt:
    pass
GPIO.cleanup() 



