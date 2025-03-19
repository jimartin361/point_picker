import vtk
import pyvista as pv
import itertools
import numpy as np
import json
import pcbnew
import math
from tkinter import simpledialog


#x_form_i = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])


class Picker:
    #def __init__(self, plotter, mesh,multi_mesh,actor_list):
    def __init__(self):
        self.plotter = None
        self.actor_list = []
        self.multi_mesh = []
        self._points = []
        self.labelled_points= []
        self.current_actor_index = 0
        self.obj_file_name = ""
        self.mtl_file_name = ""
        self.tex_path = ""
        self.x_form=None
        self.output_file = ""
        
    @property
    def points(self):
        """To access all th points when done."""
        return self._points

    def SetObjfilename(self,str_in):
        self.obj_file_name=str_in

    def SetMtlfilename(self,str_in):
        self.mtl_file_name=str_in

    def SetTextureDirectory(self,str_in):
        self.tex_path=str_in

    def SetXform(self,xform_in):
        self.x_form=xform_in

    def SetOutputFile(self,str_in):
        self.output_file=str_in
        
    
    def all_actors_red(self):
        colors=vtk.vtkNamedColors()
        for the_points in self.labelled_points:            
            #the_points['sphere_actor'].prop.color='red'
            the_points['sphere_actor'].GetProperty().SetColor(colors.GetColor3d('red'))

    def current_actor_blue(self):
        colors=vtk.vtkNamedColors()
        print(len(self.labelled_points))
        if (len(self.labelled_points)>0):
            self.labelled_points[self.current_actor_index]['sphere_actor'].GetProperty().SetColor(colors.GetColor3d('blue'))
            #print(dir(self.labelled_points[self.current_actor_index]['sphere_actor']))
            #print("just set %d to blue"%self.current_actor_index)

    def the_i_key(self):
        print("the_i_key")
        for actor in self.actor_list:
            print(actor.GetMatrix())


    def convert_vtk_matrix_4x4_to_numpy(self,vtk_in):
        out=np.ones((4,4))
        for i in range(4):
            for j in range(4):
                out[i,j]=vtk_in.GetElement(i,j)
        return out
            
            
    def get_current_object_xform(self):
        if len(self.actor_list)>0:
            first_actor_matrix=self.actor_list[0].GetMatrix()
            print(first_actor_matrix)
            retval=self.convert_vtk_matrix_4x4_to_numpy(first_actor_matrix)
            return retval
        else:
            return None
            

    def get_pyvista_plotter_object(self):
        return(self.plotter)
    

    def LoadWorkspace(self,json_fname):
        with open(json_fname,'r',encoding='utf-8') as f:
            data=json.load(f)
            self.SetObjfilename(data['obj_file_name'])
            self.SetMtlfilename(data['mtl_file_name'])
            self.SetTextureDirectory(data['tex_path'])
            self.SetXform(convert_str_list_np_array(data['x_form']))

            print(self.x_form)
            self.x_form=self.x_form
            self.plotter=pv.Plotter()
            pds,the_texs = get_meshes_and_textures_from_obj(self.obj_file_name,self.mtl_file_name,self.tex_path)
            self.multi_mesh=pds
            self.actor_list=[]
            for the_pd,the_tex in zip(pds,the_texs):
                if the_pd.number_of_points>0:
                    #self.actor_list.append(self.plotter.add_mesh(the_pd.transform(self.x_form,transform_all_input_vectors=True),texture=the_tex))
                    current_actor=self.plotter.add_mesh(the_pd,texture=the_tex)
                    self.actor_list.append(current_actor)
                    current_actor.user_matrix=self.x_form
            


            for item in data['the_points']:
                point_np=np.array([float(item['point'][0]),
                                   float(item['point'][1]),
                                   float(item['point'][2])])
                self.add_point(point_np,self.plotter,item['label_text'])


    def get_min_max(self,data):

        xmin=9e9
        xmax=-9e9
        ymin=9e9
        ymax=-9e9
    
        for item in data:
            current_x=data[item][0]
            current_y=data[item][1]       
            if current_x<xmin:
                xmin=current_x
            if current_y<ymin:
                ymin=current_y
            if current_x>xmax:
                xmax=current_x
            if current_y>ymax:
                ymax=current_y

        return([xmin,xmax,ymin,ymax])


                
    def place_points_in_kicad(self,data,output_file,rot_mat,xoffset,yoffset):
        board = pcbnew.LoadBoard('template_project.kicad_pcb')
    
        the_path="./"
    
        footprint="pogo_pin_hole"
    
        count=1
        text_xpos=30
        text_ypos=30
        for item in data:
            test_point = pcbnew.FootprintLoad(the_path,footprint)
            the_pad = test_point.GetTopLeftPad()
            #print(dir(the_pad))
            the_pad.SetDrillSizeX(720000)
            the_pad.SetDrillSizeY(720000)
            the_pad.SetNumber(count)
            xpos=rot_mat[0][0]*float(data[item][0])+rot_mat[0][1]*float(data[item][1]);
            ypos=rot_mat[1][0]*float(data[item][0])+rot_mat[1][1]*float(data[item][1]);
            xpos=float(xpos)
            ypos=float(ypos)
            test_point.SetPosition(pcbnew.wxPointMM(xpos+xoffset,ypos+yoffset))
            test_point.SetValue(item)
            test_point.SetReference("REF_%s"%item)
            board.Add(test_point)
            pcb_txt = pcbnew.PCB_TEXT(board)
            pcb_txt.SetText("%d: %s"%(count,item))
            pcb_txt.SetTextSize(pcbnew.wxSizeMM(5,5))
            pcb_txt.SetPosition(pcbnew.wxPointMM(text_xpos,text_ypos+count*6))
            pcb_txt.SetLayer(pcbnew.F_SilkS)
            board.Add(pcb_txt)      
            count=count+1

        board.Save(output_file)
                
    def output_to_kicad(self,out_file):
        the_data={}
        for the_point in self.labelled_points:
            xpos=the_point['point'][0]
            ypos=the_point['point'][1]
            zpos=the_point['point'][2]
            the_text=the_point['label_text']
            the_data[the_text]=np.array([xpos,ypos,zpos])
            
        [xmin,xmax,ymin,ymax]=self.get_min_max(the_data)
        xc = (xmax+xmin)/2.0
        yc = (ymax+ymin)/2.0
        ang=90.0*3.1415926/180.0
        flip_y_axis=np.array([[1,0],[0,-1]])
        do_rot=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
        rot_mat = np.matmul(do_rot,flip_y_axis)
        #print(rot_mat)
        #print(do_rot)
        self.place_points_in_kicad(the_data,out_file,rot_mat,float(150-xc),float(100+yc))
        
        

                
    def save_data(self,out_file):
        data_to_save=dict()
        current_xform=self.get_current_object_xform()
        if current_xform is not None:
            print("initial xform")
            print(self.x_form)
            self.x_form=current_xform
            print("current_xform")
            print(current_xform)
            
        with open(out_file,'w',encoding='utf-8') as f:
            out_data=[]
            for the_point in self.labelled_points:
                out_data.append(dict(point=[str(the_point['point'][0]),str(the_point['point'][1]),str(the_point['point'][2])],label_text=the_point['label_text']))
            print(out_data)
            data_to_save['the_points']=out_data
            data_to_save['obj_file_name']=self.obj_file_name
            data_to_save['mtl_file_name']=self.mtl_file_name
            data_to_save['tex_path']=self.tex_path
            data_to_save['x_form']=convert_np_array_to_str_list(self.x_form)
            json.dump(data_to_save,f,indent=4) 
            f.close()
            
    def the_s_key_save(self):
        print("the_s_key")
        self.save_data(self.output_file)
        self.output_to_kicad("%s.kicad_pcb"%self.output_file)
        


    def the_o_key_save_initial_workspace(self):
        #self.save_data("initial_workspace.json")
        self.save_data(self.output_file)
        
    def the_s_key_rotate_x(self):
        print("the_s_key")
        for actor in self.actor_list:
            actor.rotate_x(0.25)
        self.plotter.update()

    def the_x_key_rotate_x(self):
        print("the_x_key")
        for actor in self.actor_list:
            actor.rotate_x(-.25)  
        self.plotter.update()

    def the_y_key_rotate_y(self):
        print("the_y_key")
        for actor in self.actor_list:
            actor.rotate_y(0.25)
        self.plotter.update()
        
    
    def the_h_key_rotate_y(self):
        print("the_h_key")
        for actor in self.actor_list:
            actor.rotate_y(-0.25)  
        self.plotter.update()



    def get_point_from_text(self,target_text):
        for label in self.labelled_points:
            if label['label_text']==target_text:
                return label['point']
        return None


    def get_distance(self):
        a=self.get_point_from_text('0')
        if a is not None:
            b=self.get_point_from_text('1')
            if b is not None:
                distance_between=np.linalg.norm(a-b)
                print("distance between %f\n"%distance_between)
                return distance_between
        return None
        
    def scale_all_the_actors(self,scale):
        for actor in self.actor_list:
            actor.SetScale(scale)
        self.plotter.update()
        
        
    def the_l_key_get_distances_and_do_scaling(self):
        print("the_l_key")
        virtual_distance=self.get_distance()
       
        the_text=simpledialog.askstring("Distance","Input distance from point 0 to point 1")
        if the_text:
            the_distance=float(the_text)
          
            print(the_distance)
            print(virtual_distance)
            scale=the_distance/virtual_distance
            print(scale)
        else:
            scale=1.0
        self.scale_all_the_actors(scale)
         
        

    def the_a_key_rotate_z(self):
        for actor in self.actor_list:
            actor.rotate_z(-0.25)
        
        self.plotter.update()


    def the_z_key_rotate_z(self):
        for actor in self.actor_list:
            actor.rotate_z(0.25)
            
        self.plotter.update()
        
            
    def the_d_key(self):
       
        if self.current_actor_index>=0:
            self.current_actor_index=self.current_actor_index+1
            self.current_actor_index=self.current_actor_index % len(self.labelled_points)
        print("the_d_key",self.current_actor_index)
        self.all_actors_red()
        self.current_actor_blue()
        self.plotter.update()
        
     

    def remove_current_point(self):
        print("removing %d"%self.current_actor_index)
        self.plotter.remove_actor(self.labelled_points[self.current_actor_index]['sphere_actor'])
        self.plotter.remove_actor(self.labelled_points[self.current_actor_index]['label_actor'])
        del(self.labelled_points[self.current_actor_index])
        if (len(self.labelled_points)>0):
            self.current_actor_index=0
        else:
            self.current_actor_index=-1

    def the_space_key_clear_all_points(self):
        for point in self.labelled_points:
            self.Plotter.remove_actor(point['sphere_actor'])
            self.Plotter.remove_actor(point['label_actor'])
        self.labelled_points.clear()
        self.current_actor_index=-1
        p.update()

            
    def the_space_key_delete_current_point(self):
        print("the_space_key")
        if (len(self.labelled_points)>0):
            self.remove_current_point()
            self.all_actors_red()
            self.current_actor_blue()
            self.plotter.update()


    def get_intersection(self,vport_point,plotter,the_mesh):
        p=plotter
        normalized_point=[vport_point[0]/p.window_size[0], vport_point[1]/p.window_size[1]]

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToNormalizedViewport()
        coordinate.SetValue(normalized_point[0],normalized_point[1])
        coords = coordinate.GetComputedWorldValue(p.renderer)
        picked_pt=np.array(coords)
        direction = picked_pt -self.plotter.camera_position[0]
        direction = direction / np.linalg.norm(direction)

        start = picked_pt - 1000 * direction
        end = picked_pt + 10000 * direction
        point, ix = the_mesh.ray_trace(start,end,first_point=True)
       
        return point
        

    
        
    
        
    def get_best_intersection(self,vport_point,p):
        best_point=[]
        smallest_dist_to_camera=9e9
        #for the_mesh in self.multi_mesh:
        for actor in self.actor_list:
            the_mesh=pv.PolyData(actor.GetMapper().GetInput()).transform(self.x_form,transform_all_input_vectors=True)
            #the_pd.transform(self.x_form,transform_all_input_vectors=True)
            if the_mesh.number_of_points>3:
                point=self.get_intersection(vport_point,p,the_mesh)
                if len(point)>0:
                    vec_camera_to_point = np.array(point)-self.plotter.camera_position[0]
                    dist_to_camera=np.linalg.norm(vec_camera_to_point)
                    if (dist_to_camera<smallest_dist_to_camera):
                        best_point=point
        return best_point

    def add_point(self,point,p,label_text):
        self._points.append(point)
        sphere_actor = p.add_mesh(pv.Sphere(radius=.2).translate(point),color='red')
        label_actor = p.add_point_labels([point],[label_text])
        self.current_actor_index=len(self.labelled_points)-1
        self.labelled_points.append(dict(point=point,label_text=label_text,sphere_actor=sphere_actor,label_actor=label_actor))
        
    
    def __call__(self, *args):
        point=self.get_best_intersection(args[0],self.plotter)
        if len(point) > 0:
            label_text=simpledialog.askstring("Label","Input a label")
            if label_text:
                self.add_point(point,self.plotter,label_text)
        else:
            print("no intersection")
        self.all_actors_red()
        self.current_actor_blue()
        self.plotter.update()
        return

def convert_np_array_to_str_list(np_array_in):
    the_shape=np_array_in.shape
    retval=[['1','0','0','0'],
            ['0','1','0','0'], 
            ['0','0','1','0'],
            ['0','0','0','1']]
    print(np_array_in)
    for i in range(0, the_shape[0]):
        for j in range(0, the_shape[1]):
            retval[i][j]=str(np_array_in[i,j])
    print(retval)
    
    return(retval)


def convert_str_list_np_array(str_list_in):
    
    retval=np.array([[1.0,0.0,0.0,0.0],
                     [0.0,1.0,0.0,0.0], 
                     [0.0,0.0,1.0,0.0],
                     [0.0,0.0,0.0,1.0]])
    #print(str_list_in)
    for i in range(0, 3):
        for j in range(0, 3):
            retval[i,j]=float(str_list_in[i][j])
    
    
    return(retval)


def get_meshes_and_textures_from_obj(obj_file_name,mtl_file_name,tex_path):
    importer = vtk.vtkOBJImporter()
    importer.SetFileName(obj_file_name)
    importer.SetFileNameMTL(mtl_file_name)
    importer.SetTexturePath(tex_path)
    importer.Read()
    importer.InitializeObjectBase()
    Renderer=importer.GetRenderer()

    actors = Renderer.GetActors()
    actors.InitTraversal()

    meshs = []
    textures = []

    for a in range(actors.GetNumberOfItems()):
        actor = actors.GetNextActor()
        
        if actor.GetTexture():
            actor.GetTexture().InterpolateOn()
            the_mesh=pv.PolyData(actor.GetMapper().GetInput())
           
            meshs.append(the_mesh)
            textures.append(pv.Texture(actor.GetTexture()))


    return meshs,textures
