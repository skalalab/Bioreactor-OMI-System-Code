# -*- coding: utf-8 -*-
"""
"""

#from time import time, sleep
import pymmcore
import os
# pymmcore stage setup
# hardware_cfg = "MMConfigxystage.cfg"
#hardware_cfg = "ASIStage.cfg"
mm_directory =  r"C:\Program Files\Micro-Manager-2.0\ASIStageXYZ.cfg"
#mm_directory =  r"C:\Program Files\Micro-Manager-2.0\ASIStage.cfg"
version_info = pymmcore.CMMCore().getAPIVersionInfo()
print(version_info)
mmc = pymmcore.CMMCore()
print(mmc.getVersionInfo())
# load the device adapters
mmc.setDeviceAdapterSearchPaths([mm_directory])
mmc.loadSystemConfiguration(os.path.join(mm_directory))
# get the stage device name
xy_stage = mmc.getXYStageDevice()
z_stage = "ZStage"
mmc.setTimeoutMs(100000) #can be longer, helps pymmcore to not time out when the stage takes a while to move
print(f"XYStage Device: {xy_stage}")
    
mmc.setProperty("XYStage", "Speed-S", 1)#mm/s 7.0 is the max velocity for the current stage
# mmc.reset()
mmc.waitForDevice(xy_stage)

#define values

#well dimensions
well_length = 10 #mm
well_width = 4 #mm

# '''
#  1--------2
#  3--------4
# '''

y_interval = 0.5 #mm
num_rows = well_width / y_interval #in mm
y_pos = 0
x_max = -1000 * well_length
y_interval = y_interval * 1000
additional_run = False

# for prop in mmc.getDevicePropertyNames(xy_stage):
#     print(prop)
    
def enter_z_pos ():
    z_positions = [0, 0, 4, 4]#positive for negative 
    return z_positions

def interpolate_z(x, y, well_length, well_width, z_tl, z_tr, z_bl, z_br): #z's top left, top right, bottom left, bottom right corner
    """Bilinear interpolation of Z based on XY position."""
    well_length = well_length * -1000 #converts to um, not sure why negative, but moves the stage in the correct direction
    well_width = well_width * -1000
    x_norm = x / well_length
    y_norm = y / well_width

    z_top = z_tl + (z_tr - z_tl) * x_norm
    z_bottom = z_bl + (z_br - z_bl) * x_norm

    return z_top + (z_bottom - z_top) * y_norm

def snake_pattern (x_min, y_pos, y_interval, x_max, well_width, z_positions):
    for x in range(int(0.5 + num_rows/2)):
        # moves to the right across the slide
        mmc.setXYPosition(x_max, y_pos)
        mmc.waitForDevice(xy_stage)
        #increases the y position and moves down
        y_pos += y_interval
        #z_pos = interpolate_z(x_max, y_pos, well_length, well_width, 1, 2, 3, 4)
        #mmc.setPosition(z_stage,z_pos)
        #mmc.waitForDevice(xy_stage)
        mmc.setXYPosition(x_max, y_pos)
        mmc.waitForDevice(xy_stage)
        #moves to the left across the slide
        mmc.setXYPosition(x_min, y_pos) # this will need to be broken into steps if change the z across
        mmc.waitForDevice(xy_stage)
        #increases the y to move down
        # this is so the final iteration moves sideways and not down
        #only move y down when it will be less than or equal to the width of the slide
        if not((y_pos + y_interval) > (well_width*1000)):
            y_pos += y_interval
            z_pos = interpolate_z(x_min, y_pos, well_length, well_width, *z_positions ) #variable will replace these numbers
            mmc.setPosition(z_stage,z_pos)
            mmc.waitForDevice(xy_stage)
            mmc.setXYPosition(x_min, y_pos)
            mmc.waitForDevice(xy_stage)

    #moves left? for the final iteration if odd interval
    if num_rows % 2 == 0:
      mmc.setXYPosition(x_max, y_pos)
      mmc.waitForDevice(xy_stage)
        
def small_snake (x_min, y_interval, x_max, well_width, well_length, scan_interval, z_positions):
    num_scans = int(well_length / (1*scan_interval)) #for example 50mm / 10mm = 5 scans of 10mm squares
    mmc.setPosition(z_stage, z_positions[0])
    for count in range(num_scans):
        x_max = x_min + scan_interval * -1000# when scan interval is in mm , why 100?
        snake_pattern(x_min, 0, y_interval, x_max, well_width, z_positions)
        x_min = x_max
        #move to next initial spot for a new scan
        mmc.setXYPosition(x_min,0)
        mmc.waitForDevice(xy_stage)

        #interpolate z of new starting point
        z_pos = z_pos = interpolate_z(x_min, 0, well_length, well_width, 1, 2, 3, 4 ) #variable will replace these numbers
        mmc.setPosition(z_stage, z_pos)
        mmc.waitForDevice(xy_stage)

    
def set_zero():
    mmc.setXYPosition(0, 0)
    mmc.waitForDevice(xy_stage)

z_positions = enter_z_pos()
#snake_pattern(0, y_interval, x_max, well_width, z_pos)
small_snake(0, y_interval, x_max, well_width, well_length, 10, z_positions)


