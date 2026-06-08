# Bioreactor OMI System Code
In-progress code for the bioreactor OMI system's GUI, pump, clamps, and stage

Peristaltic_pump_clamp_control.ino is the code uploaded to the Arduino
pump_scan_control is what is run to start the process. This code interacts with the Arduino by sending serial values. It also calls methods in xyz_stage_snake_pattern
xyz_stage_snake_pattern is the code that directs the stage to move in a snake pattern. This file is called by pump_scan_control
pump_interface is the in-progress interface that can be used for the bioreactor OMI system. 
xyz_stage_snake_pattern_older is the older (not as cleaned up) version of the stage code that was used to collect data at one point. If the other code does not work, try this one.

The main code files right now are:
peristaltic_pump_clamp_control.ino
pump_scan_control.py
xyz_stage_snake_pattern.py
