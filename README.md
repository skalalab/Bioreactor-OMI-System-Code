# Bioreactor OMI System Code
In-progress code and GUI for controlling the peristaltic pump for the SEED bioreactor

Peristaltic_pump_clamp_control.ino is the code uploaded to the Arduino
pump_scan_control is what is run to start the process. This may not work with the interface well yet.
xyz_stage_snake_pattern is the code that directs the stage to move in a snake pattern. This file is called by pump_scan_control
pump_interface is the in-progress interface that can be used for the bioreactor OMI system. 
xyz_stage_snake_pattern_older is the older (not as cleaned up) version of the stage code that was used to collect data at one point. If the other code does not work, try this one.
