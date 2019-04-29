# DrawGcode
A simple program that allows the graphical preview of .gcode files by utilising pythons Pyplot library.
Mainly written for internal use in teaching the workings of G-code.

Since it is written for use with a plotter only 2D G-codes are supported. The pen is controlled via M280 P0 S? commands
S>40 is interpreted as pen down, S=0 is interpreted as pen up.

Supported commands:
G28
G1 X? Y?
G2 X? Y? I? J?
G3 X? Y? I? J?
M400
M280 P0 S?

This tool is command line only. 
To use it call the script with the filename of your .gcode as the first parameter e.g. -> python DrawGcode.py example.gcode.

Update 17.01.19
fixed an issue where a missing G28 command could crash the script.

Update 29.04.9
added a few more warnings

