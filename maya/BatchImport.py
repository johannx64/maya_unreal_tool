import maya.cmds as cmds
import os

IMPORT_PATH = r"E:\University Documents\Class Stuff (2 DAE Semester 4)\Tools & Automation\Imports\Meshes"
TEST_PATH = r"E:\University Documents\Class Stuff (2 DAE Semester 4)\Tools & Automation\Nature_Rock_vd3edgg_2K_3d_ms\vd3edgg_LOD1.fbx"
EXPORT_LOCATION = r"E:\University Documents\Class Stuff (2 DAE Semester 4)\Tools & Automation\Base Meshes\Meshes"
EXPORT_SOURCE_FILE = r"E:\University Documents\Class Stuff (2 DAE Semester 4)\Tools & Automation\scriptTesting.ma"
# import a mesh into maya - get file location


def simple_import(file_path:str):
    mesh_info = cmds.file(file_path, i = True, rnn = True)
    return mesh_info

def batch_import(file_paths:[]):
    nodes_list = []
    for file_path in file_paths:
        nodes= cmds.file(file_path, i = True, rnn = True)
        nodes_list.append(nodes)
    return nodes_list


#create a dictionary containing all the meshes intended for import - their file paths
def search_meshes(path:str, extensions: () = (".FBX", ".fbx")) -> {}:
    file_location_dict = {}
    for root, dirs, filenames in os.walk(path):
        print("root:", root)
        print("filenames", filenames)
        print("*" * 50)
        for file in filenames:
            # get the extension by getting splitting name with dot and checking the last element
            #if file.split(".")[-1] in extensions:
                # if valid extension add to dictionary where folder is the key, and value are the valid files
                # .get gives us the list of files we want to extend, if not found, gives us a new empty list
                list_ms =  file_location_dict.get(root, [])
                # add current file to list
                list_ms.append(file)
                # assign the list to the folder
                file_location_dict[root] = list_ms

    print(file_location_dict)
    return  file_location_dict

def create_import_list(meshes_location:str) -> []:
    paths_dictionary = search_meshes(meshes_location)
    import_list =[]
    for key, values in paths_dictionary.items():
        for file_name in values:
            file_name = os.path.join(key, file_name)
            import_list.append(file_name)
    return import_list


def rename_meshes(name:str)->[]:
    new_mesh_names = []
    for i, nodes_list in enumerate(meshes_nodes):
        for j, node in enumerate(nodes_list):
            if j==5:
                new_name = name + str(i+1)
                new_mesh_names.append(new_name)
                print(f"value at index ({i}, {j}): {node} ")
                cmds.rename(node, new_name)

    return new_mesh_names


#credits for making the face selection:
# https://stackoverflow.com/questions/48706280/how-to-find-y-face-of-the-cube-in-maya-with-python
#find a way to turn the tolerance variable into a slider within the ui that adjusts the amount of moss you can apply to
# a given mesh / mesh library
def modify_mesh():
    axis = (0,1,0)
    tolerance = 60
    # cmds.select(test_cube, test_rock)
    # cmds.group(test_cube, test_rock)
    #name="test_rock"
    #cmds.rename(test_rock2, name)
    for i, name in enumerate(diff_mesh_names):
        cmds.select( name + ".f[*]", r=True)
        cmds.polySelectConstraint(mode=3, type=8, orient=2, orientaxis=axis, orientbound=(0, tolerance))
        cmds.polyExtrudeFacet(kft=True, ltz=0.5)
        sel = cmds.ls(sl=True)
        create_and_assign_material(sel)
        cmds.polySelectConstraint(dis=True)
        cmds.select(cl=True)


# create and assign shader function
# https://stackoverflow.com/questions/57797087/how-do-you-apply-a-material-to-selected-faces-in-maya-using-python
def create_and_assign_material(obj_name):
    test_material = cmds.shadingNode('lambert', asShader=True, n="M_test_material")
    shading_group = cmds.sets(empty=True, renderable=True, noSurfaceShader=True)
    # connect the shader to the shading group
    cmds.connectAttr(test_material+'.outColor', shading_group + ".surfaceShader", f=True)
    cmds.sets(obj_name, forceElement = shading_group)


def export_modified_mesh():
    #cmds.select(test_cube, test_rock)
    cmds.file(EXPORT_SOURCE_FILE, typ = "FBX export", es = True)


#FUNCTION TEST RUNS
#mesh_properties = simple_import(TEST_PATH)
#print(mesh_properties)
#test_cube = cmds.polyCube(h = 1.5, n = "test_cube")
#test_rock2 = mesh_properties[5]
batch_import_list = create_import_list(IMPORT_PATH)
meshes_nodes = batch_import(batch_import_list)
diff_mesh_names = rename_meshes("SM_Rock")
modify_mesh()
#(type(test_rock2))
#export_modified_mesh()
print(meshes_nodes)
#print(meshes_nodes[0][5])
print(diff_mesh_names)


#UI
class DemoWindow(object):
    def __init__(self):
        self.window = cmds.window(t="Cool Script Name", w=500, h=500, menuBar=True)
        self.layout = cmds.formLayout(p=self.window)
        self.create_content()
        self.col_layout=cmds.columnLayout(p=self.window)


    #def choose_location_build_ui(self, *args):
        #self.root = cmds.fileDialog2(ds=2, fm=2, cap="Choose Source File")[0]
        #for dirpath, dirnames, filenames in os.walk(self.root):
            #for file in filenames:
                #if os.path.splitext(file) in (".fbx", ".FBX"):
                 # cmds.textScrollList(ai =batch_import(self.root))
       # cmds.separator(w=500, p=self.col_layout, st="in")
        #cmds.button(l="Import Meshes", p=self.col_layout, c=batch_import(self.root))

    def show(self):
        cmds.showWindow(self.window)
    def create_content(self):
        button = cmds.button(l="import", c=self._cmd_create)
        cmds.formLayout(self.layout, e=True,
        af=[(button, "top", 10),
            (button, "left", 10),
            (button, "right",10)],
        an=[(button, "bottom")])
        self.list = cmds.textScrollList(p=self.layout, w=200, selectCommand=self._cmd_select)
        cmds.formLayout(self.layout, e=True,
                        ac=[(self.list, "top", 10, button)],
                        af=[(self.list, "left", 10),
                            (self.list, "bottom", 10)],
                        an=[(self.list, "right")])

    def _cmd_create(self, _):
        pass

    def _cmd_select(self, _):
        pass

#demo = DemoWindow()
#demo.show()