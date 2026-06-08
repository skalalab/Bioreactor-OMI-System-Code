# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 10:56:40 2026

@author: admin2
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 11:51:11 2025

@author: aisaak

fix when the pump_on is lager than interval - weird behavior
figure out how to handle when the scanning time is longer than the wait time
somehow figure out how to calculate the scan time
exception handling for if stage doesn't respond or has other issues
"""
import serial
import time
from datetime import datetime, timedelta
#import time tagger code
import xyz_stage_snake_pattern as stage

# creates a serial prot object to open  a serial with an adruino on COM#
arduino = serial.Serial(port = 'COM5', baudrate=9600, timeout = .1)

#this method sends a numerical value to a serial port
def write_to(serialVal):
    #converts the inputted value back to string
    serialVal = str(serialVal) 
    #sends value to arduino as byted encoded with utf-8
    arduino.write(bytes(serialVal, 'utf-8'))
    time.sleep(0.05)
# returns a value read from the serial port
def read_from():
    #decodes the serial output from arduino
    value = arduino.readline().decode('utf-8')
    return value
'''
run_pump sends a value to the arduino that controls the pump and sends 0 (off) after waiting 
wait time. 
'''
def run_pump(val, wait, pump_on, z_pos):
  print("sending ", val, "to arduino")
  write_to(val)
  #time.sleep(0.5) #pause for aruduino to respond
  #print("Read from Arduino:", read_from())
  time.sleep(pump_on) #time the pump is on 
  print("turning off pump")
  write_to(0) #90 is the value that stops the pump from moving #0 speed
  #call scan plate (this should maybe be threaded?)
  print("waiting and scanning for ", wait,"seconds or until scanning is done")
  #should keep track of how long it takes to scan?
  start_scan = datetime.now().timestamp() * 1000
  stage.small_snakes(0, 0.5, 10, 4, 10, *z_pos) #x_min, y_interval, well_width, well_length, scan_interval, z_positions (list)) units in mm besides z_pos
  # call time tagger to start collecting data
  
  scan_time = datetime.now().timestamp() * 1000 - start_scan
  # set plate position back to 0
  print("resetting position to 0,0")
  stage.set_zero()
  #this should be changed to include the time it took to scan
  # measure the time it took to scan, then time.sleep(wait - time for scan) if negative don't wait or small wait
  if(wait - scan_time >= 0):
      time.sleep(wait) #amount to wait before interval is read again. Should be interval - time pump is on
  else:
      time.sleep(1)
  return datetime.now().replace(microsecond=0)

#-----------------main parameters------------------------#
run_time = 300 #seconds
interval = 60 #seconds
#amountDispensed = 0.2 #mL
pump_on = 5 #seconds
#--------------------------------------------------------#
#rate = 0.38 #mL/s for 70 using old arduino code
to_arduino = 0 #0 is max speed one way while 180 is max speed the other way
#pump_on = amountDispensed / rate  #amount / rate ml/s for 70 Is about 6.67
wait_time = interval - pump_on  #is about 53.33
times_run = int(run_time / interval)

#call method to find z positions and store z values

try:
    z_pos = stage.enter_z_pos()
    if(not run_time % interval == 0):
        print("The overall time cannot be divided evenly into the entered intervals.\n")
        if(run_time < interval): #maybe add + scantime
            raise ValueError("time interval cannot be larger than run time")
            
    #to_arduino = None
    start_time = datetime.now().replace(microsecond=0)
    current_interval = start_time
    end_time = start_time + timedelta(seconds = run_time)
    print("start: ", start_time)
    print("end: ", end_time)
    print(times_run, "samples will be taken over the time period")

    #user inputs the value to send to the port/arduino on the port
    #to_arduino = int(input("enter the value for speed\n"))

    # does not allow the user to sent a value outside of the range 0 - 255
    if(to_arduino is None or  to_arduino < 0): #changed upper bounds to 180 servo takes 0 - 180
        raise ValueError("Invalid speed sent to Arduino")
        # sends the input value to the Arduino if input is valid
    
    #finds how many times the pump will need to be turned on to take samples
    #at given interval for given amount of time, minus one time
    #the last iteration is out of the loop to skip the long time.sleep
    for i in range(int(run_time / interval) - 1):
        run_pump(to_arduino, wait_time, pump_on, z_pos)
        #wait until scan is done perhaps the scan can return a true when done
        #what happens if scanning time takes a long time? Have a variable for how long it takes to scan and reset?
    
    #completes the last iteration without waiting at the end
    print("sending ", to_arduino, "to arduino")
    write_to(to_arduino)
    # time.sleep(0.5) #pause for aruduino to respond
    time.sleep(pump_on) #time the pump is on  
    print("Turning off arduino")
    write_to(0)
    stage.small_snakes(0, 0.5, 10, 4, 10 *z_pos) #x_min, y_interval, well_width, well_length, z_positions (list)) units in mm besides z_pos
    stage.set_zero()
         
 # if the user enters special characters or letters, a ValueError will be 
 # raised and excepted with a message to enter only valid input, the value
 # will not be sent
 # add exception handling for if something with the setup of the stage goes wrong in the other code
except ValueError as e:
  exception_message = str(e) 
  print(f"invalid input\n{exception_message}")
#keyboard interrupt closes serial port to prevent busy serial port errors
except KeyboardInterrupt:
    print("Keyboard Interrupt, closing serial port and stopping pump")
    write_to(0)
    time.sleep(1)
    to_arduino = 0
    #arduino.close()
    stage.set_zero()
# finally:
#     arduino.close
#
# time tagger save data?
print("Program done running, closing serial port")
# once the pump is stopped the serial is closed unitl the program runs again
time.sleep(1) #if pump doesn't shut off when 0 is entered this should be a larger value
arduino.close() #closes the serial port to prevent busy serial port issues
