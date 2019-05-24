import gpiozero as gpio
import sys
import time

motors = [gpio.Motor(17, 18), gpio.Motor(22, 23), gpio.Motor(9, 25), gpio.Motor(11, 8)]

clk = 0.5

'''
instructions:

stopall
closeall
setmotor m1_speed m2_speed m3_speed m4_speed m5_speed
stopmotor m
'''

try:
    while True:
        inp = sys.stdin.readline()
        tokens = inp.split()
        
        if len(tokens) <= 0:
            continue
            
        else:
            inst_name = tokens[0]
                        
            if inst_name == 'stopall':
                for i in motors:
                    i.stop()
            elif inst_name == 'closeall':
                for i in motors:
                    i.close()
            elif inst_name == 'setmotor':
                speeds = [float(x) for x in tokens[1:]]
                                
                for i in range(len(speeds)):
                    motors[i].forward(speeds[i])
            elif inst_name == 'stopmotor':
                if len(tokens) == 2:
                    m = float(tokens)
                    motors[m].stop()
        
        time.sleep(clk)
        
        
    
except:
    for i in motors:
        i.stop()
        i.close()

