import sys  
import vtk
import numpy as np
import pyvista as pv
from tkinter import simpledialog
import itertools
from InputOutputLocal import *
import json


def print_usage():
    print("%s <json configuration file>"%sys.argv[0])
    print("right click to insert a point")
    print("left and middle clicking controls viewport rotation and translation")
    print("the d key controls which point is highlighted in blue")
    print("the s key will save the points to the json configuration file")
    print("the l key will show the distance between points labelled \"0\" and \"1\"")
    print("the spacebar will delete the point highlighted in blue")
    print("the q key will terminate the program")

picker = Picker()

if len(sys.argv)>1:
    picker.LoadWorkspace(sys.argv[1])
    picker.SetOutputFile(sys.argv[1])
    p=picker.get_pyvista_plotter_object()
    p.track_click_position(picker,side='right',viewport=True)
    p.add_key_event("d",picker.the_d_key)
    p.add_key_event("i",picker.the_i_key)
    p.add_key_event("s",picker.the_s_key_save)
    p.add_key_event("l",picker.get_distance)
    p.add_key_event("space",picker.the_space_key_delete_current_point)

    p.show_axes()
    p.show_grid()
    p.show()

else:
    print_usage()

