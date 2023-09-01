import sys  
import vtk
import numpy as np
import pyvista as pv
from tkinter import simpledialog
import itertools
from InputOutputLocal import *
import json


picker = Picker()

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

