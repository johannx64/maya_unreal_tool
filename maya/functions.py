import maya.cmds as cmds
import os
import sys

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
    def cmd_import(self, folder, fbx_files) -> None:
        """
        Command to import .fbx files into the Maya scene.
        :param folder: The folder containing the .fbx files.
        :return: None
        """
        # Append the folder path to each filename in fbx_files
        fbx_files_path = [os.path.join(folder, f) for f in fbx_files]

        if fbx_files_path:
            # Iterate over each .fbx file in the global fbx_files list
            for fbx_file in fbx_files_path:
                print(f"Importing: {fbx_file}")
                
                # Import the .fbx file into the scene
                list_nodes = cmds.file(fbx_file, i=True, type="FBX", returnNewNodes=True)
                
                # Get the transform nodes from the imported nodes
                transform_ls = cmds.ls(list_nodes, type='transform')
                
                # If you have a custom shader assignment logic, you can use it here
                for i, sel in enumerate(transform_ls):
                    print(f"Assigning shader to: {sel}")
                    assign_shaders(transform_ls, len(transform_ls), i)

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