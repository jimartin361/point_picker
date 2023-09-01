# point_picker
This is simple proof of concept Python code that uses PyVista, VTK and Tkinter
to provide an primitive interface for annotating a printed circuit board.

The code may be started with:

python pick_points.py qspi_monitor.json

The "qspi_monitor.json" file includes information on the 3D object, the transform used to display it and any annotated points.

The usage is:
pick_points.py <json configuration file>
right click to insert a point
left and middle clicking controls viewport rotation and translation
the d key controls which point is highlighted in blue
the s key will save the points to the json configuration file
the l key will show the distance between points labelled "0" and "1"
the spacebar will delete the point highlighted in blue
the q key will terminate the program



