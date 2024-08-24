import maya.cmds as cmds
import os
import sys
import random

# Constants
WINDOW_WIDTH = 600
GRID_HEIGHT = 20
MOSS_MATERIAL_NAME = "Moss"

# Global variables to hold the list of FBX files and available assets
fbx_files = []
available_assets = []
# Dictionary to store UI element references
export_ui_elements = {}

# global variables section
scatter_num_instances = 20
scatter_scale_min = 0.5
scatter_scale_max = 2.0
scatter_size = 0.5
moss_min_tolerance = 10
moss_max_tolerance = 60
moss_extrusion_scale = 0.5  # Default value, adjust as needed


# Global variable to store the Unreal export path
unreal_export_path = r"C:\Users\Acer\Documents\maya_unreal\maya_test\export_to_unreal"
scatter_assets_path = r"C:\Users\Acer\Documents\maya_unreal\maya_test\scatter_assets"
fbx_import_path = r"C:\Users\Acer\Documents\maya_unreal\maya_test"
current_project_path = fbx_import_path
# Define a custom class to hold the data for each export item
class ExportItem:
    def __init__(self, name, path, moss, plants, selected_asset):
        self.name = name
        self.path = path
        self.moss = moss
        self.plants = plants
        self.selected_asset = selected_asset

    def __repr__(self):
        return f"ExportItem(name={self.name}, path={self.path}, moss={self.moss}, plants={self.plants}, selected_asset={self.selected_asset})"


"""
Custom function to import .fbx files into the scene
"""
class ExportTools(object):
    def _fix_naming_convention(self, old_mesh_name: str, vers: str, cur_mesh) -> str:
        """
        Takes the names of meshes and returns Unreal compliant name of the mesh for exporting
        :param old_mesh_name:
        :param vers:
        :param cur_mesh:
        :return:
        """
        correct_name = self._get_mesh_names(cur_mesh)
        print(correct_name)
        full_mesh_name = str("SM" + "_" + correct_name + "_" + str(vers))
        print(full_mesh_name)

        if cmds.objExists(old_mesh_name):
            cmds.select(old_mesh_name, replace=True)
            cmds.rename(full_mesh_name)
            return full_mesh_name

    def export_meshes(self, export_location: str) -> None:
        """
        Export all mesh structs to path
        :param export_location:
        :return:
        """
        # Dictionary to store mapping between origin path and export path
        origin_export_mapping = {}

        for cur_mesh in self.imported_meshes:
            mesh_origin = r'{}'.format(str(cur_mesh.root))
            name = cur_mesh.name
            textures = cur_mesh.texture_path

            # Returns correct path
            _corrected_paths = self._check_mesh_origin(origin_export_mapping, mesh_origin, export_location, name)
            self._create_tex_folder(_corrected_paths, textures)

            for vers in cur_mesh.list_versions:
                old_mesh_name = name + "_" + vers
                fixed_names = self._fix_naming_convention(old_mesh_name, vers, cur_mesh)
                print(fixed_names)
                cmds.select(fixed_names, r=True)
                destination_path = os.path.join(_corrected_paths, fixed_names)

                cmds.file(destination_path, force=True, options="v=0;", typ="FBX export", pr=True, es=True)

class ImportTools(object):
    def cmd_import(self) -> None:
        """
        Command to import .fbx files into the Maya scene.
        :param folder: The folder containing the .fbx files.
        :return: None
        """
        # Append the folder path to each filename in fbx_files
        fbx_files_path = [os.path.join(fbx_import_path, f) for f in fbx_files]

        if fbx_files_path:
            # Iterate over each .fbx file in the global fbx_files list
            for fbx_file in fbx_files_path:
                print(f"Importing: {fbx_file}")
                
                # Import the .fbx file into the scene
                list_nodes = cmds.file(fbx_file, i=True, type="FBX", returnNewNodes=True)
                
                # Get the transform nodes from the imported nodes
                transform_ls = cmds.ls(list_nodes, type='transform')
                
                # If you have a custom shader assignment logic, you can use it here
                """
                for i, sel in enumerate(transform_ls):
                    print(f"Assigning shader to: {sel}")
                    assign_shaders(transform_ls, len(transform_ls), i)
                """
            # Return list of imported meshes to Window class
            BatchProcessorWindow._mesh_imports = fbx_files_path
            BatchProcessorWindow._import_path_executed = cmds.textField(self._import_path, q=True, tx=True)
            print(BatchProcessorWindow._mesh_imports)

            # Group meshes depending on checkboxes
            self._group_meshes()

            # Execute initialize export function
            self.export_tab._initialize_export_tab()
        else:
            print("No meshes to import, analyze folder structure first!")

class ScatterTools(object):
    def scatter_mesh_on_surface(self, surface, custom_mesh, num_instances=20, scale_variation=(1, 1), size=1.0):
        """
        Scatter instances of a custom mesh on the surface mesh.

        Parameters:
        - surface: str, name of the surface mesh to scatter objects on.
        - custom_mesh: str, name of the custom mesh to scatter.
        - num_instances: int, number of instances to scatter.
        - scale_variation: tuple of two floats, minimum and maximum scale factors.
        - size: float, size of each instance.
        """
        # Create a group to contain all instances of the custom mesh.
        group_meshes = cmds.group(empty=True, name=custom_mesh + '_grp#')

        # Get the mesh's faces.
        faces = cmds.polyEvaluate(surface, face=True)

        # Iterate through each face to determine its normal.
        upward_faces = []
        for face_id in range(faces):
            # Get the normal vector of the face.
            face_name = f"{surface}.f[{face_id}]"
            normal_info = cmds.polyInfo(face_name, faceNormals=True)
            # Ensure we have valid normal data.
            if normal_info:
                normal = normal_info[0]
                normal_vector = [float(x) for x in normal.split()[2:5]]  # Extract normal vector
                # Check if the normal is upward-facing (Y-component is positive).
                if normal_vector[1] > 0.1:  # Adjust threshold as needed.
                    upward_faces.append(face_id)

        # Scatter custom mesh on upward-facing faces.
        for _ in range(num_instances):
            obj = cmds.instance(custom_mesh)
            # Select a random face from the upward-facing list.
            face_id = random.choice(upward_faces)
            face_name = f"{surface}.f[{face_id}]"
            
            # Get the vertices of the chosen face.
            face_verts = cmds.polyListComponentConversion(face_name, ff=True, tv=True)
            face_verts = cmds.filterExpand(face_verts, sm=31) if face_verts else []
            if face_verts:
                # Average the positions of the vertices to approximate the face center.
                avg_pos = [0, 0, 0]
                for vert in face_verts:
                    pos = cmds.pointPosition(vert, w=True)
                    avg_pos = [avg_pos[i] + pos[i] for i in range(3)]
                avg_pos = [pos / len(face_verts) for pos in avg_pos]
            
                # Set the position of the object.
                cmds.xform(obj[0], ws=True, t=avg_pos)
                
                # Get the normal vector from the face.
                normal_info = cmds.polyInfo(face_name, fn=True)
                if normal_info:
                    normal_vector = [float(x) for x in normal_info[0].split()[2:5]]
                    
                    # Calculate rotation based on normal vector.
                    angle = cmds.angleBetween(euler=True, v1=(0, 1, 0), v2=normal_vector)
                    cmds.rotate(angle[0], angle[1], angle[2], obj[0])
                    
                    # Move the object slightly along the normal.
                    cmds.move(0.1 * normal_vector[0], 0.1 * normal_vector[1], 0.1 * normal_vector[2], obj[0], r=True)
                    
                    # Add random scaling and rotation for a natural appearance.
                    scale_factor = random.uniform(scale_variation[0], scale_variation[1])
                    cmds.scale(size * scale_factor, size * scale_factor, size * scale_factor, obj[0])
                    cmds.rotate(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360), obj[0], r=True)
                    
                    # Parent the custom mesh instance to the group.
                    cmds.parent(obj[0], group_meshes)

        # Parent the group of instances to the surface mesh.
        cmds.parent(group_meshes, surface)

        # Clean up history for the custom mesh.
        cmds.delete(ch=True)

        # Hide the original custom mesh
        cmds.hide(custom_mesh)

        return group_meshes, custom_mesh
    def create_and_assign_material(self, selection):
        """Create a moss material and assign it to the selected faces."""
        shader = cmds.shadingNode('lambert', asShader=True)
        shading_grp = cmds.sets(shader, edit=True, forceElement=True)
        
        # Set the color or texture of the moss material
        cmds.setAttr(shader + ".color", 0.0, 0.5, 0.0, type="double3")  # Example green color
        
        if selection:
            print(f"Assigning material to: {selection}")
            cmds.select(selection)
            cmds.hyperShade(assign=shader)
        else:
            print("No selection to assign material.")

    def get_mesh_names_from_fbx(self, fbx_files):
        """
        Convert FBX filenames to mesh names.
        :param fbx_files: List of FBX filenames.
        :return: List of mesh names (stripping the '.fbx' extension).
        """
        mesh_names = [os.path.splitext(os.path.basename(fbx))[0] for fbx in fbx_files]
        print(f"Mesh names extracted from FBX files: {mesh_names}")
        return mesh_names

    def add_moss(self, fbx_files, min_tolerance=10, max_tolerance=60, extrusion_scale=0.5, material_name="MossMaterial"):
            """
            Apply moss effect to the specified meshes.
            :param fbx_files: List of FBX filenames to apply the effect to.
            :param min_tolerance: Minimum value for random tolerance.
            :param max_tolerance: Maximum value for random tolerance.
            :param extrusion_scale: Scale factor for moss extrusion.
            :param material_name: Name of the material to apply to the extruded faces.
            """
            mesh_names = self.get_mesh_names_from_fbx(fbx_files)
            
            for name in mesh_names:
                print(f"Processing mesh: {name}")
                
                # Generate a random tolerance value
                tolerance = random.uniform(min_tolerance, max_tolerance)
                print(f"Using tolerance: {tolerance}")
                
                # Select all faces of the mesh
                if not cmds.objExists(name):
                    print(f"Mesh {name} does not exist in the scene.")
                    continue
                
                cmds.select(name + ".f[*]", r=True)
                selection = cmds.ls(sl=True)
                
                if not selection:
                    print(f"No faces selected for mesh: {name}")
                    continue
                
                try:
                    # Apply polySelectConstraint with random tolerance
                    cmds.polySelectConstraint(mode=3, type=8, orient=2, orientaxis=(0,1,0), orientbound=(0, tolerance))
                    
                    # Use the extrusion_scale parameter for the extrusion
                    cmds.polyExtrudeFacet(kft=True, ltz=extrusion_scale)
                    
                    # Get the selected faces after extrusion
                    sel = cmds.ls(sl=True)
                    
                    if sel:
                        print(f"Faces selected for extrusion: {sel}")
                    else:
                        print(f"No faces found after extrusion for mesh: {name}")
                    
                    # Create and assign material
                    self.create_and_assign_green_material(sel, material_name)
                    
                except TypeError as e:
                    print(f"Error applying effect to mesh {name}: {e}")
                
                finally:
                    # Clear selection and disable polySelectConstraint
                    cmds.polySelectConstraint(dis=True)
                    cmds.select(cl=True)
                    print(f"Completed processing for mesh: {name}")

    def create_and_assign_green_material(self, objects, material_name):
        """
        Create a green material and assign it to the given objects.
        :param objects: List of objects to assign the material to.
        :param material_name: Name of the material to create.
        """
        # Check if the material already exists
        if not cmds.objExists(material_name):
            # Create a new lambert material
            material = cmds.shadingNode('lambert', asShader=True, name=material_name)
            
            # Set the color to green
            cmds.setAttr(material + ".color", 0, 0.5, 0, type="double3")
        else:
            material = material_name

        # Assign the material to the objects
        for obj in objects:
            cmds.select(obj)
            cmds.hyperShade(assign=material)

        print(f"Green material '{material_name}' created and assigned to extruded faces.")


def move_pivot_to_bottom_center(mesh_name):
    # Ensure the object exists
    if not cmds.objExists(mesh_name):
        print(f"Object '{mesh_name}' does not exist.")
        return
    
    # Select the mesh
    cmds.select(mesh_name)
    
    # Get the bounding box of the mesh
    bbox = cmds.exactWorldBoundingBox(mesh_name)
    print(f"Original bounding box: {bbox}")
    
    # Calculate the bottom center position
    min_x, min_y, min_z, max_x, max_y, max_z = bbox
    center_x = (min_x + max_x) / 2
    center_y = min_y
    center_z = (min_z + max_z) / 2
    print(f"Calculated bottom center: ({center_x}, {center_y}, {center_z})")
    
    # Move the pivot to the bottom center
    cmds.move(center_x, center_y, center_z, mesh_name + ".scalePivot", relative=True, a=True)
    cmds.move(center_x, center_y, center_z, mesh_name + ".rotatePivot", relative=True, a=True)
    
    # Verify the new pivot position
    new_scale_pivot = cmds.xform(mesh_name + ".scalePivot", query=True, ws=True, rp=True)
    new_rotate_pivot = cmds.xform(mesh_name + ".rotatePivot", query=True, ws=True, rp=True)
    print(f"New scale pivot position: {new_scale_pivot}")
    print(f"New rotate pivot position: {new_rotate_pivot}")

# Function to get the name of the first mesh in the scene
def find_mesh_by_name_in_scene(fbx_filename):
    # Extract the base name without extension and adjust it dynamically
    base_name = os.path.splitext(fbx_filename)[0]
    
    # List all mesh shapes in the scene
    all_meshes = cmds.ls(type='mesh')
    
    # Check if the base name is contained in the mesh names
    for mesh in all_meshes:
        transform_node = cmds.listRelatives(mesh, parent=True)
        if transform_node:
            transform_name = transform_node[0]
            if base_name in transform_name:
                return transform_name
    
    return None 
# Create an instance of ImportTools
import_tools = ImportTools()
# create an instance of ScatterTools
scatter_tools = ScatterTools()

def remove_extension(filename):
    # Split the filename and its extension
    base, ext = os.path.splitext(filename)
    return base

def browse_folder():
    """Browse for a folder containing .fbx files."""
    global fbx_import_path
    folder = cmds.fileDialog2(fileMode=3, caption="Select Folder")[0]
    if folder:
        fbx_import_path = folder
        cmds.textField('fbxImportPath', edit=True, text=folder)
        populate_fbx_list(folder)

def populate_fbx_list(folder):
    """Populate the list with .fbx files from the selected folder."""
    global fbx_files
    fbx_files = [f for f in os.listdir(folder) if f.endswith('.fbx')]
    refresh_import_list()
    refresh_export_list()

def browse_assets_folder():
    """Browse for a folder containing assets to scatter/age."""
    global scatter_assets_path
    folder = cmds.fileDialog2(fileMode=3, caption="Select Assets Folder")[0]
    if folder:
        scatter_assets_path = folder
        cmds.textField('scatterAssetsPath', edit=True, text=folder)
        populate_assets_list(folder)

def populate_assets_list(folder):
    """Populate the list with assets from the selected folder."""
    global available_assets
    available_assets = [f for f in os.listdir(folder) if f.endswith('.fbx')]
    refresh_assets_list()

def refresh_import_list():
    """Refresh the import list UI."""
    global fbx_files  # Ensure you're referencing the global fbx_files variable
    
    # Clear the existing items in the import list UI
    cmds.textScrollList('importList', edit=True, removeAll=True)
    
    # Add the updated list of .fbx files to the UI
    for fbx_file in fbx_files:
        cmds.textScrollList('importList', edit=True, append=fbx_file)
def clear_export_items():
    global export_ui_elements
    for element in export_ui_elements.values():
        cmds.deleteUI(element, control=True)
    export_ui_elements.clear()


def refresh_assets_list():
    """Refresh the assets list UI."""
    cmds.textScrollList('assetsList', edit=True, removeAll=True)
    for asset in available_assets:
        cmds.textScrollList('assetsList', edit=True, append=asset)

def remove_selected_import():
    """Remove selected items from the import list."""
    selected_items = cmds.textScrollList('importList', query=True, selectItem=True)
    global fbx_files
    fbx_files = [fbx for fbx in fbx_files if fbx not in selected_items]
    refresh_import_list()
    refresh_export_list()

def select_all_items(asset_list):
    """Select all items in the asset list."""
    all_items = cmds.textScrollList(asset_list, query=True, allItems=True)
    if all_items:
        cmds.textScrollList(asset_list, edit=True, selectItem=all_items)

def remove_from_export_list(fbx):
    """Remove an item from the export list and UI."""
    global fbx_files
    # Remove the item from the fbx_files list
    if fbx in fbx_files:
        fbx_files.remove(fbx)
    
    # Remove the item from the export_ui_elements dictionary
    if fbx in export_ui_elements:
        del export_ui_elements[fbx]

    # Refresh the export UI
    refresh_export_list()
    refresh_import_list()

def update_scatter_num_instances(*args):
    global scatter_num_instances
    scatter_num_instances = cmds.intSliderGrp('scatterNumInstances', query=True, value=True)

def update_scatter_scale_min(*args):
    global scatter_scale_min
    scatter_scale_min = cmds.floatSliderGrp('scatterScaleMin', query=True, value=True)

def update_scatter_scale_max(*args):
    global scatter_scale_max
    scatter_scale_max = cmds.floatSliderGrp('scatterScaleMax', query=True, value=True)

def update_scatter_size(*args):
    global scatter_size
    scatter_size = cmds.floatSliderGrp('scatterSize', query=True, value=True)

def update_moss_min_tolerance(*args):
    global moss_min_tolerance
    moss_min_tolerance = cmds.floatSliderGrp('mossMinTolerance', query=True, value=True)

def update_moss_max_tolerance(*args):
    global moss_max_tolerance
    moss_max_tolerance = cmds.floatSliderGrp('mossMaxTolerance', query=True, value=True)

def update_moss_extrusion_scale(*args):
    global moss_extrusion_scale
    moss_extrusion_scale = cmds.floatSliderGrp('mossExtrusionScale', query=True, value=True)

def create_import_ui(root):
    """Create the import UI section."""
    frame = cmds.frameLayout(p=root, label="FBX Importer", width=WINDOW_WIDTH, collapsable=True, collapse=False)
    column = cmds.columnLayout(p=frame, adjustableColumn=True)
    cmds.textField('fbxImportPath', text=fbx_import_path, editable=False, parent=column)
    cmds.button(label="Browse Folder", parent=column, command=lambda _: browse_folder())
    #Import the Stuff
    cmds.button(label="Import Files", parent=column, command=lambda _: import_tools.cmd_import())
    cmds.textScrollList('importList', parent=column, height=80) 
    if fbx_import_path:
        cmds.textField('fbxImportPath', edit=True, text=fbx_import_path)
        populate_fbx_list(fbx_import_path)

def create_assets_ui(root):
    """Create the assets selection UI section."""
    frame = cmds.frameLayout(p=root, label="Scatter/Aging Assets", width=WINDOW_WIDTH, collapsable=True, collapse=False)
    column = cmds.columnLayout(p=frame, adjustableColumn=True)
    cmds.textField('scatterAssetsPath', text=scatter_assets_path, editable=False, parent=column)
    cmds.button(label="Select Assets Folder", parent=column, command=lambda _: browse_assets_folder())
    cmds.textScrollList('assetsList', parent=column, height=80)
    if scatter_assets_path:
        cmds.textField('scatterAssetsPath', edit=True, text=scatter_assets_path)
        populate_assets_list(scatter_assets_path)

def create_export_ui():
    """Create the export UI section."""
    if cmds.frameLayout('exportFrame', exists=True):
        cmds.deleteUI('exportFrame', layout=True)

    export_frame = cmds.frameLayout('exportFrame', p='mainLayout', label="Export Items", width=WINDOW_WIDTH, collapsable=True, collapse=False)
    export_column = cmds.columnLayout(p=export_frame, adjustableColumn=True)
    
    # Scatter Controls
    scatter_frame = cmds.frameLayout(p=export_column, label="Scatter Controls", collapsable=True, collapse=False)
    scatter_column = cmds.columnLayout(p=scatter_frame, adjustableColumn=True)
    cmds.intSliderGrp('scatterNumInstances', label='Number of Instances', field=True, minValue=1, maxValue=100, value=scatter_num_instances, changeCommand=update_scatter_num_instances)
    cmds.floatSliderGrp('scatterScaleMin', label='Min Scale', field=True, minValue=0.1, maxValue=5.0, value=scatter_scale_min, changeCommand=update_scatter_scale_min)
    cmds.floatSliderGrp('scatterScaleMax', label='Max Scale', field=True, minValue=0.1, maxValue=5.0, value=scatter_scale_max, changeCommand=update_scatter_scale_max)
    cmds.floatSliderGrp('scatterSize', label='Size', field=True, minValue=0.1, maxValue=5.0, value=scatter_size, changeCommand=update_scatter_size)

    # Moss Controls
    moss_frame = cmds.frameLayout(p=export_column, label="Moss Controls", collapsable=True, collapse=False)
    moss_column = cmds.columnLayout(p=moss_frame, adjustableColumn=True)
    cmds.floatSliderGrp('mossMinTolerance', label='Min Tolerance', field=True, minValue=0, maxValue=90, value=moss_min_tolerance, changeCommand=update_moss_min_tolerance)
    cmds.floatSliderGrp('mossMaxTolerance', label='Max Tolerance', field=True, minValue=0, maxValue=200, value=moss_max_tolerance, changeCommand=update_moss_max_tolerance)
    cmds.floatSliderGrp('mossExtrusionScale', label='Moss Extrusion', field=True, minValue=0.1, maxValue=10.0, value=moss_extrusion_scale, changeCommand=update_moss_extrusion_scale)

    # Export Items List
    items_frame = cmds.frameLayout(p=export_column, label="Export Items List", collapsable=True, collapse=False)
    items_column = cmds.columnLayout(p=items_frame, adjustableColumn=True)
    
    # Column headers
    cmds.rowLayout(numberOfColumns=6, adjustableColumn=3, columnWidth6=[50, 50, 250, 200, 100, 100], parent=items_column)
    cmds.text(label="Moss", align='center')
    cmds.text(label="Plants", align='center')
    cmds.text(label="FBX Name", align='center')
    cmds.text(label="Scatter Assets", align='center')
    cmds.text(label="Select All", align='center')
    cmds.text(label="Remove", align='center')

    for fbx_file in fbx_files:
        row = cmds.rowLayout(numberOfColumns=6, adjustableColumn=3, columnWidth6=[50, 50, 250, 200, 100, 100], parent=items_column)
        
        moss_checkbox = cmds.checkBox(label="", value=True, parent=row)
        plants_checkbox = cmds.checkBox(label="", value=True, parent=row)
        name_label = cmds.text(label=fbx_file, align='left', parent=row)
        asset_list = cmds.textScrollList(allowMultiSelection=True, height=60, append=available_assets, parent=row)

        # Select all items by default
        select_all_items(asset_list)

        # Store references to UI elements
        export_ui_elements[fbx_file] = {
            'moss': moss_checkbox,
            'plants': plants_checkbox,
            'name': name_label,
            'asset_list': asset_list
        }

        # "Select All" button for the asset list within the row
        cmds.button(label="Select All", parent=row, command=lambda x, list=asset_list: select_all_items(list))
                
        # "Remove" button for the row
        cmds.button(label="Remove", parent=row, command=lambda x, fbx=fbx_file: remove_from_export_list(fbx))
def refresh_export_list():
    """Refresh the export list UI."""
    # Clear existing export UI elements
    if cmds.frameLayout('exportFrame', exists=True):
        cmds.deleteUI('exportFrame', layout=True)
    
    # Recreate the export UI
    create_export_ui()

def refresh_import_list():
    """Refresh the import list UI."""
    global fbx_files
    
    cmds.textScrollList('importList', edit=True, removeAll=True)
    
    for fbx_file in fbx_files:
        cmds.textScrollList('importList', edit=True, append=fbx_file)
    
    # Only refresh the export list if it has changed
    if set(fbx_files) != set(export_ui_elements.keys()):
        refresh_export_list()

def browse_unreal_folder():
    """Browse for a folder to export to Unreal."""
    global unreal_export_path
    folder = cmds.fileDialog2(fileMode=3, caption="Select Unreal Export Folder")[0]
    if folder:
        unreal_export_path = folder
        cmds.textField('unrealExportPath', edit=True, text=folder)
import maya.cmds as cmds

def extract_base_name(asset_name):
    """Extract the base name from the asset file name."""
    # Remove the prefix (e.g., SM_) and the extension (.fbx)
    base_name = asset_name.split('_', 1)[-1]  # Remove prefix
    base_name = base_name.rsplit('.', 1)[0]  # Remove file extension
    
    # Optionally, remove any suffix after the last underscore
    base_name = base_name.rsplit('_', 1)[0]
    
    return base_name.lower()  # Convert to lowercase for case-insensitive comparison

def find_similar_mesh(asset_name):
    """Find a mesh in the scene with a name similar to the given asset name."""
    # Extract the base name from the asset name
    base_name = extract_base_name(asset_name)
    
    # Get all meshes in the scene
    mesh_list = cmds.ls(type="mesh", long=True)
    
    # Iterate through the meshes and find one with a similar name
    for mesh in mesh_list:
        # Get the transform node (the parent of the mesh)
        transform_node = cmds.listRelatives(mesh, parent=True)
        if transform_node:
            transform_name = transform_node[0]
            # Convert transform name to lowercase for comparison
            if base_name in transform_name.lower():
                return transform_name  # Return the transform node name
    
    return None  # No similar mesh found

def export_to_unreal():
    """Export each mesh individually to the specified Unreal export path."""
    global export_ui_elements, scatter_num_instances, scatter_scale_min, scatter_scale_max, scatter_size, moss_min_tolerance, moss_max_tolerance, moss_extrusion_scale

    if not unreal_export_path:
        cmds.warning("Please select an export folder for Unreal first.")
        return

    # Ensure the export path exists
    if not os.path.exists(unreal_export_path):
        os.makedirs(unreal_export_path)

    scatter_tools = ScatterTools()
    original_meshes_to_delete = []

    # Loop through each FBX file and export it
    for fbx_file, elements in export_ui_elements.items():
        export_items = []  # Collect items to print later
        
        # Define the source path of the FBX file
        source_path = os.path.join(current_project_path, fbx_file)
        
        # Use the export prefix
        destination_filename = os.path.splitext(fbx_file)[0] + ".fbx"
        destination_path = os.path.join(unreal_export_path, destination_filename)

        # Query UI elements for current FBX file
        moss_value = cmds.checkBox(elements['moss'], query=True, value=True)
        plants_value = cmds.checkBox(elements['plants'], query=True, value=True)
        name_value = cmds.text(elements['name'], query=True, label=True)
        selected_assets = cmds.textScrollList(elements['asset_list'], query=True, selectItem=True)
        
        export_item = {
            'name': name_value,
            'moss': moss_value,
            'plants': plants_value,
            'selected_assets': selected_assets
        }

        # Append to export items list
        export_items.append(export_item)
        
        # Open the file to apply effects and export
        if os.path.exists(source_path):
            try:
                # Open the file
                cmds.file(source_path, open=True, force=True)
                
                # Get the mesh names from the scene
                mesh_list = cmds.ls(type="mesh")
                surface_mesh = mesh_list[0]
                print(f"Mesh names extracted from FBX files: {mesh_list}")

                for mesh in mesh_list:
                    print(f"Processing mesh: {mesh}")
                    # Apply moss effect if moss is checked
                    if moss_value:
                        try:
                            scatter_tools.add_moss([mesh], min_tolerance=moss_min_tolerance, max_tolerance=moss_max_tolerance, extrusion_scale=moss_extrusion_scale, material_name=MOSS_MATERIAL_NAME)
                            print(f"Applied moss effect to {mesh} with tolerance range {moss_min_tolerance} - {moss_max_tolerance} and extrusion scale {moss_extrusion_scale}")
                        except Exception as e:
                            print(f"Failed to apply moss effect to {mesh}: {str(e)}")

                    # Scatter objects if plants are checked
                    if plants_value:
                        try:
                            for asset in selected_assets:
                                # Construct the full path for each scatter asset
                                asset_path = os.path.join(scatter_assets_path, asset)
                                if os.path.exists(asset_path):
                                    # Import the FBX file
                                    cmds.file(asset_path, i=True, type="FBX", mergeNamespacesOnClash=False, namespace=":")
                                    scatter_asset_name = find_similar_mesh(asset)
                                    group_meshes, original_mesh = scatter_tools.scatter_mesh_on_surface(
                                        surface=surface_mesh[:-5],
                                        custom_mesh=scatter_asset_name,
                                        num_instances=scatter_num_instances,
                                        scale_variation=(scatter_scale_min, scatter_scale_max),
                                        size=scatter_size
                                    )
                                    original_meshes_to_delete.append(original_mesh)
                            print(f"Scattered objects on {mesh}")
                        except Exception as e:
                            print(f"Failed to scatter objects on {mesh}: {str(e)}")

                # Ensure that all changes are saved before exporting
                cmds.file(rename=destination_path)
                cmds.file(save=True, type='FBX export')
                
                print(f"Exported {fbx_file} to {destination_path}")

            except Exception as e:
                print(f"Failed to export {fbx_file}: {str(e)}")
        else:
            print(f"Source file {source_path} does not exist.")

    # Clean up original meshes used for scattering
    for mesh in original_meshes_to_delete:
        if cmds.objExists(mesh):
            cmds.delete(mesh)

    # Print the collected export items
    print("Collected Export Items:")
    for item in export_items:
        print(item)

    cmds.confirmDialog(title="Export Complete", message="Files exported to Unreal successfully!", button=["OK"])

def create_unreal_export_ui(root):
    """Create the Unreal export UI section."""
    frame = cmds.frameLayout(p=root, label="Export to Unreal", width=WINDOW_WIDTH)
    column = cmds.columnLayout(p=frame, adjustableColumn=True)
    cmds.textField('unrealExportPath', text=unreal_export_path, editable=False, parent=column)
    cmds.button(label="Browse Folder", parent=column, command=lambda _: browse_unreal_folder())
    cmds.button(label="Export to Unreal!", parent=column, command=lambda _: export_to_unreal())
    if unreal_export_path:
        cmds.textField('unrealExportPath', edit=True, text=unreal_export_path)

def create_ui():
    """Create the main UI window."""
    if cmds.window("myWindow", exists=True):
        cmds.deleteUI("myWindow", window=True)

    window = cmds.window("myWindow", title="FBX Batch Import/Export", widthHeight=(WINDOW_WIDTH, 700), sizeable=True)
    cmds.columnLayout('mainLayout', adjustableColumn=True)
    
    # Create Scatter/Aging Assets, Import, and Export sections
    create_assets_ui('mainLayout')
    create_import_ui('mainLayout')
    create_export_ui()

    # Add the new Unreal export section
    create_unreal_export_ui('mainLayout')

    cmds.showWindow(window)

create_ui()
