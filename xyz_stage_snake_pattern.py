import pymmcore
import os
# ----------- setup ----------- #
# directory for the micro manager configuration of the stage device
mm_directory =  r"C:\Program Files\Micro-Manager-2.0\ASIStageXYZ.cfg"
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
mmc.waitForDevice(xy_stage)
# ----------------------------- #

# this prints some properties that can be coded / changed
# for prop in mmc.getDevicePropertyNames(xy_stage):
#     print(prop)

# parameters #
# Speed
mmc.setProperty("XYStage", "Speed-S", 1) # mm/s 7.0 is the max velocity for the stage
# well dimensions
well_length = 1 #mm
well_width = 4 #mm
y_interval = 0.5 #mm 
y_pos = 0 #initial y position
# x_max = -1000 * well_length
'''
enter_z_pos is in progress
'''
def enter_z_pos ():
    # '''
    #  index of list Z_positions and related corners
    #  0--------1
    #  2--------3
    # '''    
    z_positions = []
    #z1 = int(input("enter the top z position"))
   # z_positions.append(z1)
    # z_positions = [0, 0, 4, 4]# positive values entered leads to negative z 
    z_positions = [0, 0, -4, -4]
    return z_positions

def interpolate_z(x, y, well_length, well_width, z_tl, z_tr, z_bl, z_br): #z's top left, top right, bottom left, bottom right corner
    """Bilinear interpolation of Z based on XY position."""
    # well_length = well_length * -1000 #converts to um, not sure why negative, but moves the stage in the correct direction
    # well_width = well_width * -1000
    well_length = well_length * 1000 #converts to um
    well_width = well_width * 1000
    x_norm = x / well_length
    y_norm = y / well_width

    z_top = z_tl + (z_tr - z_tl) * x_norm
    z_bottom = z_bl + (z_br - z_bl) * x_norm

    return z_top + (z_bottom - z_top) * y_norm

'''
snake_pattern creates a snake pattern that ranges from from x_min to x_max
and iterates y_pos by y_interval until the max y coordinate is reached

----
   |
----  if num_rows is one, this is the last time the stage moves for a snake iteration
|
---- this line is not repeated in the loop, only the prior ones are
'''
def snake_pattern (x_min, x_max, y_interval, y_pos, well_width, z_positions):
    num_rows = well_width / y_interval #in mm
    # each iteration completes two rows, forward and backward (/2)
    # for x in range(int(0.5 + num_rows/2)):
    for x in range(int(num_rows/2)):
        # moves to the right across the slide
        mmc.setXYPosition(x_max, y_pos)
        mmc.waitForDevice(xy_stage)
        #increases the y position and moves down
        y_pos += y_interval
        mmc.setXYPosition(x_max, y_pos)
        mmc.waitForDevice(xy_stage)
        #moves to the left across the slide
        mmc.setXYPosition(x_min, y_pos) # this will need to be broken into steps if change the z across
        mmc.waitForDevice(xy_stage)
        # this is so the final iteration does not move downwards after moving sideways
        # only moved y down when it will be less than or equal to the width of the slide
        #if not((y_pos + y_interval) > (well_width*1000)):
        if (y_pos + y_interval) <= (well_width * 1000):
            #i ncreases the y to move down
            y_pos += y_interval
            z_pos = interpolate_z(x_min, y_pos, well_length, well_width, *z_positions ) 
            mmc.setPosition(z_stage,z_pos)
            mmc.waitForDevice(xy_stage)
            mmc.setXYPosition(x_min, y_pos)
            mmc.waitForDevice(xy_stage)
    # final iteration if even number of rows
    if num_rows % 2 == 0:
      mmc.setXYPosition(x_max, y_pos)
      mmc.waitForDevice(xy_stage)

'''
small_snakes calls snake_pattern a number of times defined by how big the snakes are (scan_interval) 
and how large the well is (well_width and well_length) to traverse the well with several small snake patterns
'''
def small_snakes (x_min, y_interval, well_width, well_length, scan_interval, z_positions):
    # unit conversions
    x_min = x_min * -1000
    y_interval = y_interval * 1000
    #sets to initial z positions and calculates the number of snake scans that will occur
    num_scans = int(well_length / (scan_interval)) #for example 50mm length / 10mm intervals = 5 scans of 10mm squares
    mmc.setPosition(z_stage, z_positions[0])
    # this loop creates snake scans across the well. The user defines the interval which determines how many 
    # snake scans occur and how many time the loop runs.
    # the count variable is not used
    for count in range(num_scans):
        # sets the max x value to the interval of snake scans that was set by the user
        x_max = x_min + scan_interval * -1000
        snake_pattern(x_min, x_max,  y_interval, 0, well_width, z_positions)
        # sets the previous max x value to the new minimum
        x_min = x_max
        #move to next initial spot for a new scan
        mmc.setXYPosition(x_min,0)
        mmc.waitForDevice(xy_stage)
        #interpolate z of new starting point
        z_pos = interpolate_z(x_min, 0, well_length, well_width, *z_positions) 
        mmc.setPosition(z_stage, z_pos)
        mmc.waitForDevice(xy_stage)
'''
moves the stage to the position (0,0)
'''
def set_zero():
    mmc.setXYPosition(0, 0)
    mmc.waitForDevice(xy_stage)

#z_positions = enter_z_pos()
#snake_pattern(0, y_interval, x_max, well_width, z_pos)
#small_snakes(0, y_interval, well_width, well_length, 10, z_positions)
