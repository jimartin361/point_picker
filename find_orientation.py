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
p.add_key_event("s",picker.the_s_key_rotate_x)
p.add_key_event("l",picker.the_l_key_get_distances_and_do_scaling)
p.add_key_event("a",picker.the_a_key_rotate_z)
p.add_key_event("space",picker.the_space_key_clear_all_points)
p.add_key_event("z",picker.the_z_key_rotate_z)
p.add_key_event("x",picker.the_x_key_rotate_x)
p.add_key_event("o",picker.the_o_key_save_initial_workspace)
p.add_key_event("y",picker.the_y_key_rotate_y)
p.add_key_event("h",picker.the_h_key_rotate_y)



p.show_axes()
p.show_grid()
p.show()

