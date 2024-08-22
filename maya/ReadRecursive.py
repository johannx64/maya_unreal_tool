import os
import maya.cmds as cmds
import colorsys
import maya.OpenMaya as om
# from functools import partial
import shutil

ROOT_PATH = r"/home/stefanstgs/Game"

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

SMALL_OFFSET = 10
NO_OFFSET = 0

TEX_ABSOLUTE_TARGET_DEFAULT = 1024
TEX_RELATIVE_DEFAULT = .5


class MeshStruct(object):
    def __init__(self, n, r, ext, vs, t_path) -> None:
        self.name = n
        self.root = r
        self.extension = ext
        self.list_versions = vs
        self.texture_path = t_path

    def get_path_lists(self) -> []:
        """
        :return: full path to all mesh variations list
        """
        list_paths = []
        for vers in self.list_versions:
            # rejoining the current version in the list and the file extension to get original name
            full_name = self.name + "_" + vers + "." + self.extension
            # joining the root and file safely using the os.path.join()
            full_path = os.path.join(self.root, full_name)
            # print(self.name, vers)
            # print(full_path, '  ' + '   ', full_name)
            list_paths.append(full_path)

        # returns list of paths
        return list_paths


class Info(object):
    """
    Info class, holds details for textSList master selection
    """

    def __init__(self, name: str, details: []):
        self.name = name
        self.details = details


class TexturesTab(object):
    def __init__(self, parent, tab_label: str) -> None:
        self.root = cmds.formLayout(parent=parent)
        cmds.tabLayout(parent, e=True, tl=(self.root, tab_label))  # , bgc=(0,1,0)
        self._create_ui()

    def _initialize_textures(self):
        self._info_list = []
        self.imported_meshes = BatchProcessorWindow._mesh_imports

    def _create_ui(self):
        mesh_textures = cmds.image(p=self.root, image='/home/stefanstgs/Pictures/Screenshots/a.png')


class ExportTab(object):
    def __init__(self, parent, tab_label) -> None:
        self.root = cmds.formLayout(parent=parent)
        cmds.tabLayout(parent, e=True, tl=(self.root, tab_label))  # , bgc=(0,1,0)
        self.selected_index = None
        self._create_ui()
        # self.image = om.MImage()

    def _create_ui(self):
        _export_description = cmds.text(p=self.root, l='Export Asset/Textures Path:')
        cmds.formLayout(self.root, e=True,

                        af=[
                            (_export_description, "top", SMALL_OFFSET),
                            (_export_description, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (_export_description, "bottom")
                        ])
        _btn_browser = cmds.button(p=self.root, l="Browse...", c=self._cmd_browser)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (_btn_browser, "top", SMALL_OFFSET, _export_description),
                        ],
                        af=[

                            (_btn_browser, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (_btn_browser, "left"),
                            (_btn_browser, "bottom")
                        ])
        self.export_path = cmds.textField(p=self.root, tx='/home/stefanstgs/Desktop/master',
                                          tcc=self._cmd_change_path)
        # cmds.textField(self.path, e=True, )
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.export_path, "top", SMALL_OFFSET, _export_description),
                            (self.export_path, "right", SMALL_OFFSET, _btn_browser)
                        ],
                        af=[

                            (self.export_path, "left", SMALL_OFFSET)

                        ],
                        an=[

                            (self.export_path, "bottom")
                        ])
        separator_export = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')  # , bgc=(1,0,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_export, "top", SMALL_OFFSET, self.export_path)
                        ],
                        af=[
                            (separator_export, "left", SMALL_OFFSET),
                            (separator_export, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_export, "bottom")
                        ])
        _mesh_list_title = cmds.text(p=self.root, l='Mesh Groups:')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (_mesh_list_title, "top", SMALL_OFFSET, separator_export),

                        ],
                        af=[
                            (_mesh_list_title, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (_mesh_list_title, "bottom")
                        ])
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self._list_export_objects = cmds.textScrollList(p=self.root, selectCommand=self._cmd_select)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._list_export_objects, "top", SMALL_OFFSET, _mesh_list_title)
                        ],
                        af=[
                            (self._list_export_objects, "left", SMALL_OFFSET),

                            (self._list_export_objects, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self._list_export_objects, "bottom"),
                        ])

        # # Add a horizontal separator after the detail panel
        separator_lists = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')  # , bgc=(1,0,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_lists, "top", SMALL_OFFSET, self._list_export_objects)
                        ],
                        af=[
                            (separator_lists, "left", SMALL_OFFSET),
                            (separator_lists, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_lists, "bottom")
                        ])
        self._details = DetailPanel(self)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._details.root, "top", SMALL_OFFSET, self._list_export_objects)
                        ],
                        af=[
                            (self._details.root, "left", SMALL_OFFSET),
                            (self._details.root, "right", SMALL_OFFSET),
                            (self._details.root, "bottom", 150)
                        ],
                        an=[

                        ])

        separator_details = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_details, "top", SMALL_OFFSET, self._details.root)
                        ],
                        af=[
                            (separator_details, "left", SMALL_OFFSET),
                            (separator_details, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_details, "bottom")
                        ])

        _rename_mesh_groups = cmds.text(p=self.root, l='Rename selected object group to:')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (_rename_mesh_groups, "top", SMALL_OFFSET, separator_details),
                        ],
                        af=[

                            (_rename_mesh_groups, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (_rename_mesh_groups, "right"),
                            (_rename_mesh_groups, "bottom")
                        ])

        self.asset_prefix = cmds.textField(p=self.root, tx='MESH_GRP_NAME', tcc=self._cmd_change_asset_name)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.asset_prefix, "top", SMALL_OFFSET, separator_details),

                            (self.asset_prefix, "left", SMALL_OFFSET, _rename_mesh_groups)
                        ],
                        af=[
                            (self.asset_prefix, "right", SMALL_OFFSET)

                        ],
                        an=[

                            (self.asset_prefix, "bottom")
                        ])

        separator_tex = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')  # , bgc=(1,0,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_tex, "top", SMALL_OFFSET, self.asset_prefix)
                        ],
                        af=[
                            (separator_tex, "left", SMALL_OFFSET),
                            (separator_tex, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_tex, "bottom")
                        ])

        self.chk_btn_resize_tex = cmds.checkBox(p=self.root,
                                                label='Resize textures: ', onc=self._cmd_resize_tex_onc,
                                                ofc=self._cmd_resize_tex_ofc)  # , changeCommand=self._coi()
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.chk_btn_resize_tex, "top", SMALL_OFFSET, separator_tex)
                        ],
                        af=[
                            (self.chk_btn_resize_tex, "left", SMALL_OFFSET),

                        ],
                        an=[
                            (self.chk_btn_resize_tex, "right"),
                            (self.chk_btn_resize_tex, "bottom")
                        ])

        self._tex_absolute_target = cmds.textField(p=self.root, tx=TEX_ABSOLUTE_TARGET_DEFAULT, ed=False)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._tex_absolute_target, "top", SMALL_OFFSET, separator_tex),

                            (self._tex_absolute_target, "left", SMALL_OFFSET, self.chk_btn_resize_tex),
                            (self._tex_absolute_target, "right", SMALL_OFFSET, self.asset_prefix)
                        ],
                        af=[

                        ],
                        an=[

                            (self._tex_absolute_target, "bottom")
                        ])

        self.chk_btn_use_relative = cmds.checkBox(p=self.root, label="Use relative", ed=False,
                                                  onc=self._cmd_resize_rel_tex_onc, ofc=self._cmd_resize_rel_tex_ofc)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.chk_btn_use_relative, "top", SMALL_OFFSET, separator_tex),
                            (self.chk_btn_use_relative, "left", SMALL_OFFSET, self._tex_absolute_target)
                        ],
                        af=[

                        ],
                        an=[
                            (self.chk_btn_use_relative, "right"),
                            (self.chk_btn_use_relative, "bottom")
                        ])

        self._tex_relative_factor = cmds.textField(p=self.root, tx=TEX_RELATIVE_DEFAULT,
                                                   tcc=self._cmd_change_asset_name, ed=False)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._tex_relative_factor, "top", SMALL_OFFSET, separator_tex),

                            (self._tex_relative_factor, "left", SMALL_OFFSET, self.chk_btn_use_relative),
                            (self._tex_relative_factor, "right", SMALL_OFFSET, self.asset_prefix)
                        ],
                        af=[

                        ],
                        an=[

                            (self._tex_relative_factor, "bottom")
                        ])

        separator_export = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')  # , bgc=(1,0,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_export, "top", SMALL_OFFSET, self.chk_btn_resize_tex)
                        ],
                        af=[
                            (separator_export, "left", SMALL_OFFSET),
                            (separator_export, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_export, "bottom")
                        ])

        btn_export = cmds.button(p=self.root, label="Export files", command=self._cmd_export)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (btn_export, "top", SMALL_OFFSET, separator_export)
                        ],
                        af=[
                            (btn_export, "right", SMALL_OFFSET),
                            (btn_export, "left", SMALL_OFFSET)

                        ],
                        an=[
                            (btn_export, "bottom")
                        ])
    def _cmd_resize_rel_tex_onc(self, _):
        cmds.textField(self._tex_relative_factor, e=True, ed=True)
        cmds.textField(self._tex_absolute_target, e=True, ed=False)
    def _cmd_resize_rel_tex_ofc(self, _):
        cmds.textField(self._tex_relative_factor, e=True, ed=False)
        cmds.textField(self._tex_absolute_target, e=True, ed=True)
    def _cmd_resize_tex_onc(self, _):
        cmds.textField(self._tex_absolute_target, e=True, ed=True)
        cmds.checkBox(self.chk_btn_use_relative, e=True, ed=True)
    def _cmd_resize_tex_ofc(self, _):
        cmds.textField(self._tex_absolute_target, e=True, ed=False)
        cmds.checkBox(self.chk_btn_use_relative, e=True, v=False)
        cmds.textField(self._tex_relative_factor, e=True, ed=False)
        cmds.checkBox(self.chk_btn_use_relative, e=True, ed=False)
    def _initialize_export_tab(self) -> None:
        self._info_list = []
        self.imported_meshes = BatchProcessorWindow._mesh_imports

        self.refresh_details()

    def refresh_details(self) -> None:
        export_path = cmds.textField(self.export_path, q=True, tx=True)
        self._info_list.clear()

        if cmds.textScrollList(self._list_export_objects, q=True, ni=True) > 0:
            cmds.textScrollList(self._list_export_objects, e=True, ra=True)

        for cur_mesh in self.imported_meshes:
            name = self._get_mesh_names(cur_mesh)
            mesh_info = self._get_mesh_info(cur_mesh, export_path)

            self._append_mesh_info(name, mesh_info)

    def _cmd_change_path(self, _) -> None:
        self.refresh_details()

    def _cmd_change_asset_name(self, _) -> None:
        if self.selected_index is None:
            print("Select a mesh to rename!")
            return

        name_new = cmds.textField(self.asset_prefix, q=True, tx=True)
        selected_mesh = self.imported_meshes[self.selected_index - 1]
        old_name = selected_mesh.name

        for vers in selected_mesh.list_versions:
            old_mesh = old_name + "_" + vers
            new_mesh = name_new + "_" + vers
            print(old_mesh)
            if cmds.objExists(old_mesh):
                cmds.rename(old_mesh, new_mesh)
            else:
                print("Mesh not found:", old_mesh)

        # Update the old_name after renaming all versions
        selected_mesh.name = name_new

        self.refresh_details()
        self._update_info_details()

    def _cmd_select(self) -> []:
        index = cmds.textScrollList(self._list_export_objects, q=True, selectIndexedItem=True)
        if index:
            self.selected_index = index[0]
            self._update_info_details()
            # self.asset_prefix  = self.imported_meshes[self.selected_index].name
        return index

    def _update_info_details(self) -> None:
        if self.selected_index is None: return

        info = self._info_list[self.selected_index - 1]
        print("Selected {} at position {}".format(info.name, info.details))
        self._details.show(info)

    def _get_mesh_names(self, cur_mesh) -> str:
        name = cur_mesh.name.capitalize() if cur_mesh.name[0].islower() else cur_mesh.name
        if not name.startswith("SM_"):
            name = "SM_" + name
        if name.startswith("SM_"):
            name = name.replace("SM_", "")
        return name

    def _get_mesh_info(self, cur_mesh, path: str) -> []:
        # print(path)
        versions = []
        name = self._get_mesh_names(cur_mesh)
        # path = cmds.textField(self.export_path, q=True, tx=True)
        # path = cmds.textField(self.export_path, q=True, tx=True)
        for vers in cur_mesh.list_versions:
            mesh_info = r"{}/{}/SM_{}_".format(path, name, name)

            vers_numeric = mesh_info + vers
            # version_with_name = f"{name}_{vers_numeric}"
            versions.append(vers_numeric)
        return versions

    def _append_mesh_info(self, name, versions) -> None:
        cmds.textScrollList(self._list_export_objects, e=True, append=name)
        info = Info(name, versions)
        self._info_list.append(info)
        self._details.show(info)

    def _cmd_export(self, _) -> None:
        if BatchProcessorWindow._import_path_executed != cmds.textField(self.export_path, q=True, tx=True): # do not poop where we eat
            print(cmds.textField(self.export_path, q=True, tx=True))
            export_location = cmds.textField(self.export_path, q=True, tx=True)  # self._export_path

            self.export_meshes(export_location)
        else:
            print("Export path identical to import path, please change!")

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

    def _create_tex_folder(self, mesh_type_folder, textures) -> None:
        # Create a folder named "Tex" for textures
        tex_folder = os.path.join(mesh_type_folder, "Tex")
        if not os.path.exists(tex_folder):
            os.makedirs(tex_folder)

        # Get the resizing option
        use_relative_factor = cmds.checkBox(self.chk_btn_use_relative, q=True, v=True)

        # Copy texture files to the export location
        for texture_path in textures:
            if os.path.exists(texture_path):
                texture_filename = os.path.basename(texture_path)
                filename, extension = os.path.splitext(texture_filename)

                if use_relative_factor:
                    # Get the relative factor
                    relative_factor = float(cmds.textField(self._tex_relative_factor, q=True, tx=True))

                    self.image = om.MImage()
                    self.image.readFromFile(texture_path)

                    # Get the original width and height
                    width = om.MScriptUtil()
                    height = om.MScriptUtil()
                    width_ptr = width.asUintPtr()
                    height_ptr = height.asUintPtr()
                    self.image.getSize(width_ptr, height_ptr)
                    orig_width = width.getUint(width_ptr)
                    orig_height = height.getUint(height_ptr)

                    # Calculate new width and height based on relative factor while maintaining aspect ratio
                    new_width = int(orig_width * relative_factor)
                    new_height = int(orig_height * relative_factor)

                    self.image.resize(new_width, new_height, True)
                else:
                    # Use absolute resizing target
                    absolute_target = int(cmds.textField(self._tex_absolute_target, q=True, tx=True))

                    self.image = om.MImage()
                    self.image.readFromFile(texture_path)

                    # Resize the image with absolute target
                    self.image.resize(absolute_target, absolute_target, True)

                # Ensure all filenames start with 'T_'
                if filename.startswith('TX_'):
                    new_filename = 'T_' + filename[3:]
                else:
                    new_filename = 'T_' + filename if not filename.startswith('T_') else filename

                # Find the last underscore
                last_underscore_index = new_filename.rfind('_')

                if last_underscore_index != -1:
                    # Extract the suffix
                    suffix = new_filename[last_underscore_index + 1:]

                    # Correct the suffix if needed
                    # Define mapping
                    mapping = {
                        'A': '_BC',
                        'ALB': '_BC',
                        'AORH': '_RMA',
                        'RMA': '_RMA',
                        'N': '_N',
                        'NRM': '_N',
                        'AORO': '_RMA'
                    }
                    if suffix in mapping:
                        new_filename = new_filename[:last_underscore_index] + '_' + mapping[suffix]

                resize_tex_bool = cmds.checkBox(self.chk_btn_resize_tex, q=True, v=True)

                # Save the resized texture to the "Tex" folder
                if resize_tex_bool:
                    resized_texture_path = os.path.join(tex_folder, new_filename + extension)
                    self.image.writeToFile(resized_texture_path, 'png')
                else:
                    shutil.copy(texture_path, os.path.join(tex_folder, new_filename + extension))

        # fileNodes = cmds.ls(sl=True)

    def _check_mesh_origin(self, origin_export_mapping, mesh_origin, export_location, name) -> str:
        # Check if the origin path already exists in the mapping
        if mesh_origin in origin_export_mapping:
            mesh_type_folder = origin_export_mapping[mesh_origin]
        else:
            mesh_type_folder = os.path.join(export_location, name)
            origin_export_mapping[mesh_origin] = mesh_type_folder

            if not os.path.exists(mesh_type_folder):
                os.makedirs(mesh_type_folder)
        return r'{}'.format(str(mesh_type_folder))

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

    def _cmd_browser(self, _) -> None:
        # Open a directory browser dialog
        selected_directory = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="Select Directory")
        if selected_directory:
            cmds.textField(self.export_path, e=True, tx=selected_directory[0])
            return selected_directory[0]  # Return the selected directory path

        else:
            return None  # Return None if no directory is selected or dialog is canceled


class DetailPanel(object):
    def __init__(self, demo_window) -> None:
        self._master = demo_window
        self.root = cmds.formLayout(p=demo_window.root)  # , bgc=(0,1,0)
        self._create_content()

    def _create_content(self) -> None:
        self._fld_name = cmds.text(p=self.root, l='')
        cmds.formLayout(self.root, e=True,
                        af=[
                            (self._fld_name, "top", SMALL_OFFSET),
                            (self._fld_name, "left", SMALL_OFFSET),
                            (self._fld_name, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self._fld_name, "bottom")
                        ])

        self._fld_nr = cmds.textScrollList(p=self.root)  # , bgc=(0,1,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._fld_nr, "top", SMALL_OFFSET, self._fld_name),
                        ],
                        af=[

                            (self._fld_nr, "left", NO_OFFSET),
                            (self._fld_nr, "bottom", NO_OFFSET),
                            (self._fld_nr, "right", NO_OFFSET)
                        ],
                        an=[

                        ])

        # self._btn_del = cmds.button(l="Delete", c=self._master.delete, en=False)
        # cmds.formLayout(self.root, e=True,
        #                 ac=[
        #
        #                 ],
        #                 af=[
        #                     (self._btn_del, "top", SMALL_OFFSET),
        #                     (self._btn_del, "right", SMALL_OFFSET),
        #                     (self._fld_nr, "right", NO_OFFSET)
        #                 ],
        #                 an=[
        #                     (self._btn_del, "bottom")
        #                 ])

    def show(self, info):
        # cmds.button(self._btn_del, e=True, en=True)
        # cmds.textScrollList(p=self.root, w=200) #, selectCommand=self._cmd_select

        if cmds.textScrollList(self._fld_nr, q=True, ni=True) > 0:
            # Clear the list
            cmds.textScrollList(self._fld_nr, e=True, ra=True)

        self._fld_name = cmds.text(self._fld_name, e=True, label=info.name)
        self._fld_nr = cmds.textScrollList(self._fld_nr, e=True, append=info.details)

    def reset(self):

        # cmds.button(self._btn_del, e=True, en=False)  # , en=False
        self._fld_name = cmds.text(self._fld_name, e=True, label="")

        if cmds.textScrollList(self._fld_nr, q=True, ni=True) > 0:
            # Clear the list
            cmds.textScrollList(self._fld_nr, e=True, ra=True)


class ImportTab(object):
    def __init__(self, parent, tab_label) -> None:

        self.root = cmds.formLayout(parent=parent)
        cmds.tabLayout(parent, e=True, tl=(self.root, tab_label))  # , bgc=(0,1,0)

        self._create_ui()
        self._info_list = []
        self._list_mesh_objects = []
        self.group_assets = False

    def _create_ui(self) -> None:

        _description_import_path = cmds.text(p=self.root, l='Root Asset Path:')
        cmds.formLayout(self.root, e=True,
                        af=[
                            (_description_import_path, "top", SMALL_OFFSET),
                            (_description_import_path, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (_description_import_path, "bottom"),
                            (_description_import_path, "right")
                        ])
        _btn_browser = cmds.button(p=self.root, l="Browse...", c=self._cmd_browser)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (_btn_browser, "top", SMALL_OFFSET, _description_import_path),
                        ],
                        af=[

                            (_btn_browser, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (_btn_browser, "left"),
                            (_btn_browser, "bottom")
                        ])

        self._btn_analyze = cmds.button(p=self.root, l="Analyze files", c=self._cmd_analyze)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._btn_analyze, "top", SMALL_OFFSET, _btn_browser),
                        ],
                        af=[
                            (self._btn_analyze, "right", SMALL_OFFSET),
                            (self._btn_analyze, "left", SMALL_OFFSET)
                        ],
                        an=[

                            (self._btn_analyze, "bottom")
                        ])

        self._import_path = cmds.textField(p=self.root, tx=ROOT_PATH)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._import_path, "top", SMALL_OFFSET, _description_import_path),
                            (self._import_path, "right", SMALL_OFFSET, _btn_browser)
                        ],
                        af=[
                            (self._import_path, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (self._import_path, "bottom")
                        ])

        separator_analyze = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_analyze, "top", SMALL_OFFSET, self._btn_analyze)
                        ],
                        af=[
                            (separator_analyze, "left", SMALL_OFFSET),
                            (separator_analyze, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_analyze, "bottom")
                        ])

        _description_mesh_objects = cmds.text(p=self.root, l='Mesh Groups:')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (_description_mesh_objects, "top", SMALL_OFFSET, separator_analyze),
                        ],
                        af=[
                            (_description_mesh_objects, "left", SMALL_OFFSET)
                        ],
                        an=[
                            (_description_mesh_objects, "bottom")
                        ])

        self._btn_del = cmds.button(l="Delete", c=self.delete, en=True)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._btn_del, "top", NO_OFFSET, separator_analyze)
                        ],
                        af=[
                            (self._btn_del, "right", SMALL_OFFSET),
                            (self._btn_del, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self._btn_del, "bottom")
                        ])

        self._mesh_objects_list = cmds.textScrollList(p=self.root,
                                                      selectCommand=self._cmd_select)  # , selectCommand=self._cmd_select,bgc=(0, 1, 0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._mesh_objects_list, "top", SMALL_OFFSET, _description_mesh_objects)
                        ],
                        af=[
                            (self._mesh_objects_list, "left", SMALL_OFFSET),

                            (self._mesh_objects_list, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self._mesh_objects_list, "bottom"),
                        ])

        separator_lists = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')  # , bgc=(1,0,0)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_lists, "top", SMALL_OFFSET, self._mesh_objects_list)
                        ],
                        af=[
                            (separator_lists, "left", SMALL_OFFSET),
                            (separator_lists, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (separator_lists, "bottom")
                        ])

        # Detail textSList of mesh object master textSList
        self._details = DetailPanel(self)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._details.root, "top", SMALL_OFFSET, self._mesh_objects_list)
                        ],
                        af=[
                            (self._details.root, "left", SMALL_OFFSET),
                            (self._details.root, "right", SMALL_OFFSET),
                            (self._details.root, "bottom", 150)
                        ],
                        an=[

                        ])

        separator_group = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_group, "top", SMALL_OFFSET, self._details.root)
                        ],
                        af=[
                            (separator_group, "left", SMALL_OFFSET),
                            (separator_group, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (separator_group, "bottom")
                        ])

        self.chk_btn_group_meshes = cmds.checkBox(p=self.root, label='Group meshes together')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.chk_btn_group_meshes, "top", SMALL_OFFSET, separator_group)
                        ],
                        af=[
                            (self.chk_btn_group_meshes, "left", SMALL_OFFSET),
                            (self.chk_btn_group_meshes, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self.chk_btn_group_meshes, "bottom")
                        ])

        self.chk_btn_grou_mesh_structs = cmds.checkBox(p=self.root,
                                                       label='Group objects together')  # , changeCommand=self._coi()
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self.chk_btn_grou_mesh_structs, "top", SMALL_OFFSET, self.chk_btn_group_meshes)
                        ],
                        af=[
                            (self.chk_btn_grou_mesh_structs, "left", SMALL_OFFSET),
                            (self.chk_btn_grou_mesh_structs, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (self.chk_btn_grou_mesh_structs, "bottom")
                        ])

        separator_import = cmds.separator(p=self.root, h=SMALL_OFFSET, w=WINDOW_WIDTH, st='single')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (separator_import, "top", SMALL_OFFSET, self.chk_btn_grou_mesh_structs)
                        ],
                        af=[
                            (separator_import, "left", SMALL_OFFSET),
                            (separator_import, "right", SMALL_OFFSET)

                        ],
                        an=[
                            (separator_import, "bottom")
                        ])

        self._btn_import = cmds.button(p=self.root, label="Import files", command=self.cmd_import)
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._btn_import, "top", SMALL_OFFSET, separator_import)
                        ],
                        af=[
                            (self._btn_import, "right", SMALL_OFFSET),
                            (self._btn_import, "left", SMALL_OFFSET)

                        ],
                        an=[
                            (self._btn_import, "bottom")
                        ])
        self._group_name = cmds.textField(p=self.root, tx='Imported Assets')
        cmds.formLayout(self.root, e=True,
                        ac=[
                            (self._group_name, "top", SMALL_OFFSET, separator_group),

                            (self._group_name, "left", SMALL_OFFSET, _description_import_path)
                        ],
                        af=[
                            (self._group_name, "right", SMALL_OFFSET)
                        ],
                        an=[
                            (self._group_name, "bottom")
                        ])

    def _cmd_analyze(self, _) -> None:
        """
        Command to analyze provided folder structure
        :param _:
        :return:
        """

        # take path from textF
        import_path = cmds.textField(self._import_path, q=True, tx=True)
        # get the dictionary
        dict_paths = search_meshes(import_path)
        # get the meshStruct list
        list_meshes = create_mesh_structs(dict_paths)
        self._list_mesh_objects = list_meshes

        # Check if the textS list is not empty
        if cmds.textScrollList(self._mesh_objects_list, q=True, ni=True) > 0:
            # Clear the list
            cmds.textScrollList(self._mesh_objects_list, e=True, ra=True)

        # for each mesh version, fill details
        for cur_mesh in self._list_mesh_objects:
            # print(cur_mesh.texture_path)
            paths = cur_mesh.get_path_lists()
            name = cur_mesh.name
            # for detail panel in import tab we use import path and imported meshes
            info = Info(name, paths)
            self._info_list.append(info)

            # for each mesh display a selectable structure
            cmds.textScrollList(self._mesh_objects_list, e=True, append=name)
        # self.cmd_import(self)

    def delete(self, _) -> None:
        """
        Delete selected mesh structure
        :param _:
        :return:
        """
        if self._cmd_select() is None:
            print("First select a mesh to delete it!")
            return

        if self._list_mesh_objects:
            index = cmds.textScrollList(self._mesh_objects_list, q=True, selectIndexedItem=True)
            print(index[0] - 1)
            del (self._info_list[index[0] - 1])
            print("deleted :", self._list_mesh_objects[index[0] - 1])
            del (self._list_mesh_objects[index[0] - 1])

            cmds.textScrollList(self._mesh_objects_list, e=True,
                                removeIndexedItem=index)  # Remove the selected mesh structure

            self._details.reset()

        else:
            print("No meshes to delete, analyze folder structure first!")
        # self._details.reset()


    def _cmd_select(self) -> []:
        index = cmds.textScrollList(self._mesh_objects_list, q=True, selectIndexedItem=True)
        if index:
            info = self._info_list[index[0] - 1]
            print("selected {} at position {}".format(info.name, info.details))
            self._details.show(info)
            return index
        else:
            index = None
            return index

    def cmd_import(self, _) -> None:
        """
        Command to import
        :param _:
        :return:
        """
        if self._list_mesh_objects:
            cmds.button(self._btn_analyze, e=True, en=False)
            cmds.button(self._btn_del, e=True, en=False)
            cmds.button(self._btn_import, e=True, en=False)
            # currently I get mesh to import from the list of meshes directly. save the modified list in the delete button function, so I can return also to export tab. then I can apply same logic on export
            for cur_mesh in self._list_mesh_objects:
                print("----------------------------------")
                list_nodes = MayaStuff.import_files(cur_mesh.get_path_lists())
                print("-----------------NODES-----------------")
                print(list_nodes)
                print("-----------------")
                # get the transform nodes from the created nodes
                for i, sel in enumerate(list_nodes):
                    print("-----------------transform_ls-----------------")
                    transform_ls = MayaStuff.filter_transform_nodes(sel)
                    print(transform_ls)
                    print("------")
                    assign_shaders(transform_ls, len(list_nodes), i)

            # return list of imported meshes to Window class
            BatchProcessorWindow._mesh_imports = self._list_mesh_objects
            BatchProcessorWindow._import_path_executed = cmds.textField(self._import_path, q=True, tx=True)
            print(BatchProcessorWindow._mesh_imports)

            # group meshes depending on checkboxes
            self._group_meshes()

            # Execute initialize export function
            self.export_tab._initialize_export_tab()
        else:
            print("No meshes to import, analyze folder structure first!")

    def set_export_tab(self, export_tab) -> None:
        """
        Initialize export tab after import
        :param export_tab:
        :return:
        """
        self.export_tab = export_tab

    def _group_meshes(self) -> None:
        group_meshes_bool = cmds.checkBox(self.chk_btn_group_meshes, q=True, v=True)
        group_mesh_structs_bool = cmds.checkBox(self.chk_btn_grou_mesh_structs, q=True, v=True)
        self._group_assets(group_meshes_bool, group_mesh_structs_bool)

    def _group_assets(self, group_meshes_bool: bool, group_mesh_structs_bool: bool) -> None:
        """
        Group all meshes
        :param group_meshes_bool:
        :param group_mesh_structs_bool:
        :return:
        """
        imported_assets_group = None

        if group_meshes_bool:
            imported_assets_group = cmds.group(em=True, name=cmds.textField(self._group_name, q=True, tx=True))

        for cur_mesh in self._list_mesh_objects:
            if group_mesh_structs_bool:
                self._group_mesh_structs(cur_mesh)

            if imported_assets_group:
                for vers in cur_mesh.list_versions:
                    if not (group_meshes_bool and group_mesh_structs_bool):
                        cmds.parent(cur_mesh.name + "_" + vers, imported_assets_group, relative=True)

        # Special case handling when both booleans are true
        if group_meshes_bool and group_mesh_structs_bool:
            for mesh_structs in self._list_mesh_objects:
                cmds.parent(mesh_structs.name, imported_assets_group, relative=True)

    def _group_mesh_structs(self, mesh_structs) -> None:
        """
        Groups by mesh structs
        :param mesh_structs:
        :return:
        """
        group_mesh_structs = cmds.group(em=True, name=mesh_structs.name)
        for vers in mesh_structs.list_versions:
            cmds.parent(mesh_structs.name + "_" + vers, group_mesh_structs, relative=True)

    def _cmd_browser(self, _) -> None:
        # Open a directory browser dialog
        selected_directory = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="Select Directory")
        if selected_directory:
            cmds.textField(self._import_path, e=True, tx=selected_directory[0])
            return selected_directory[0]  # Return the selected directory path

        else:
            return None  # Return None if no directory is selected or dialog is canceled


class BatchProcessorWindow(object):
    def __init__(self) -> None:
        self._win = cmds.window(t="Batch processor", w=WINDOW_WIDTH, h=WINDOW_HEIGHT, mb=True)

        self._create_menu()

        self._create_content()
        self._create_tabs()

        self._mesh_imports = []
        self._import_path_executed = None

    def show(self):
        cmds.showWindow(self._win)

    def _create_content(self):
        self.root = cmds.formLayout(p=self._win)

    def _create_tabs(self) -> None:
        self._tabs = cmds.tabLayout(p=self.root)
        cmds.formLayout(self.root, edit=True,
                        af=[
                            (self._tabs, "top", NO_OFFSET),
                            (self._tabs, "right", NO_OFFSET),
                            (self._tabs, "left", NO_OFFSET),
                            (self._tabs, "bottom", NO_OFFSET)
                        ])
        name = "Import"
        self.import_tab = ImportTab(self._tabs, name)
        # name = "Textures" # an idea to make a window to be able to resize texture per group or maybe even per mesh and having them displayed
        # self.textures_tab = TexturesTab(self._tabs, name)
        name = "Export"
        self.export_tab = ExportTab(self._tabs, name)
        #
        self.import_tab.set_export_tab(self.export_tab)

    # CREATE MENU FOR UI
    def _create_menu(self):
        menu_file = cmds.menu(p=self._win, label="File")
        cmds.menuItem(parent=menu_file, label="New", command=self._cmd_new)
        cmds.menuItem(parent=menu_file, label="Open...")
        cmds.menuItem(parent=menu_file, divider=True)

        self._menu_save = cmds.menuItem(parent=menu_file, label="Save", enable=False)
        cmds.menuItem(parent=menu_file, label="Save as...", command=self._cmd_save_as)
        cmds.menuItem(parent=menu_file, divider=True)
        cmds.menuItem(parent=menu_file, label="Exit", command=self._cmd_exit)

        edit_menu = cmds.menu(p=self._win, l="Edit", tearOff=True)
        cmds.menuItem(p=edit_menu, label="Enable compatibility", checkBox=False, c=self._cmd_enable_compatibility)
        cmds.menuItem(p=edit_menu, label="Use long names", checkBox=True)

        cmds.menuItem(parent=edit_menu, divider=True)

        preferences_menu = cmds.menuItem(p=edit_menu, l="Preferences", subMenu=True, tearOff=True)
        cmds.menuItem(p=preferences_menu, l='Modeling')
        cmds.menuItem(p=preferences_menu, l='Animation')
        cmds.menuItem(p=preferences_menu, l='Rendering')

        cmds.menuItem(parent=edit_menu, divider=True)

        cmds.menuItem(p=edit_menu, l='Reset')
        cmds.menuItem(p=edit_menu, optionBox=True, c=self._cmd_reset_more)

    # ...MENUBAR FUNCTIONS
    def _cmd_new(self, _):
        print("Creating something new")

    # DO THIS TO EXECUTE BUTTON COMMAND AS FUNCTION
    def _cmd_save_as(self, _):
        cmds.menuItem(self._menu_save, e=True, enable=True)

    # DO THIS TO QUIT UI
    def _cmd_exit(self, _):
        cmds.deleteUI(self._win)

    # DO THIS TO EXECUTE THE BUTTON
    def _cmd_enable_compatibility(self, selected):
        print("Compatibility: {}".format(selected))

    def _cmd_reset_more(self, _):
        print("Opening up reset menu more")


# get dict
# dict_paths = search_meshes(ROOT_PATH) first line ; uses provided root
def search_meshes(path: str, extensions: () = ("FBX", "obj", "fbx")) -> {}:
    """
    Searches meshes from a root folder
    :param path: root path
    :param extensions: possible extensions to search for files
    :return: dictionary of folders with list of meshes
    """
    dict_meshes = {}
    # goes over every folder (root) and lists all the sub folders (dir) and files (filenames)
    for root, dirs, filenames in os.walk(path):
        print("root:", root)
        print("dirs:", dir)
        print("filenames", filenames)
        print("*" * 50)
        for file in filenames:
            # get the extension by getting splitting name with dot and checking the last element
            if file.split(".")[-1] in extensions:
                # if valid extension add to dictionary where folder is the key, and value are the valid files
                # .get gives us the list of files we want to extend, if not found, gives us a new empty list
                list_ms = dict_meshes.get(root, [])
                # print(list_ms)
                # add current file to list
                list_ms.append(file)
                # print(list_ms)

                # assign the list to the folder
                dict_meshes[root] = list_ms
                # print(dict_meshes[root])

    return dict_meshes


def search_textures(path: str, image_extensions: tuple = ("PNG", "jpg", "png", "JPG", "exr", "EXR")) -> list:
    """
    Searches textures from analyzed folder path
    :param path:
    :param image_extensions:
    :return:
    """
    # Initialize an empty list to store texture file paths
    texture_files = []
    # Determine the path separator based on whether the input path contains forward slashes or backslashes
    separator = '/' if '/' in path else '\\'
    # Split the path into root and tail
    textures_root = path.rsplit(separator, 1)[0]
    # Walk through the directory tree starting from textures_root
    for root, dirs, filenames in os.walk(textures_root):
        for file in filenames:
            if file.split(".")[-1].lower() in image_extensions:
                # Construct the full path to the texture file
                texture_file = os.path.join(root, file)
                print(texture_file)
                texture_files.append(texture_file)

    return texture_files


# populate info class function,
def create_mesh_structs(mesh_dict) -> []:
    """
    Create a list of meshes with versions
    :param mesh_dict: dictionary of folders as keys with list of the meshes inside of it as values
    :return: list of mesh structures
    """
    mesh_structs = []
    print("-----------------MESH_GROUPS-----------------")
    for key, values in mesh_dict.items():
        # get image files (complete path to each texture of a mesh  group)
        image_files = search_textures(r'{}'.format(str(key)))

        for file_name in values:
            root = key

            # remove the extension by splitting(".") and rejoining(".") all but last element
            n_without_ext = ".".join(file_name.split(".")[:-1])
            name = "_".join(n_without_ext.split("_")[:-1])

            # empty variable to see if we found an existing mesh to add variations to it
            ms = None
            # get the variation number
            variation = n_without_ext.split("_")[-1]
            # loop over the list of meshes we encountered
            for mesh in mesh_structs:
                # if there is a mesh already with the same name and location we need to add variation to it
                if mesh.name == name and mesh.root == root:
                    ms = mesh

            # if there is none, create new mesh with this being the first variation
            if ms is None:
                ext = file_name.split(".")[-1]
                ms = MeshStruct(name, root, ext, [variation], image_files)
                mesh_structs.append(ms)
                print(ms.name)  # + " " + textures_root
                print("Textures of mesh group")
                print(ms.texture_path)
                print("-----------------")
            else:
                # else add the variation to it
                ms.list_versions.append(variation)

    return mesh_structs


class MayaStuff(object):
    def __init__(self, path_lists: [], nodes_list: []):
        pass

    #
    # import file
    def import_files(path_lists: []) -> []:
        """
        List of paths to import
        :param path_lists: full paths to file
        :return: list of created nodes for every imported file
        """
        list_of_nodes = []
        # for every file, get the new nodes created from it
        for path in path_lists:
            nodes = cmds.file(path, i=True, rnn=True)
            list_of_nodes.append(nodes)

        # print(list_of_nodes)
        return list_of_nodes

    # filter transform nodes
    def filter_transform_nodes(nodes_list: []) -> []:
        """
        Filter transform nodes from imported nodes, also hides and ignores UCX
        :param nodes_list: list of imported nodes
        :return: list of transform nodes
        """
        transform_list = []
        for node in nodes_list:
            # check if the first character is vertical line
            if node[0] == "|":
                # ignore the child nodes that have been added by only checking single parent nodes
                splits = node.split("|")
                if len(splits) == 2:
                    # get the second element as the name starts with |, split makes first element empty
                    transform = splits[1]
                    # ignore UCX and set them hidden
                    # print(transform)
                    if transform[0:3] == "UCX":
                        cmds.setAttr(transform + ".visibility", 0)
                    else:
                        transform_list.append(transform)

        # print(transform_list)
        return transform_list


def create_shader(name, clr, mat_type="lambert"):
    """
    Create and assigns material to given transform
    :param name: name of the transform node
    :param clr: color of the shader
    :param mat_type: material type
    :return:
    """
    # create the material
    material = cmds.shadingNode(mat_type, name="mat_" + name, asShader=True)
    # set the color of the material
    cmds.setAttr(material + ".color", clr[0], clr[1], clr[2], type="double3")
    # create surfaceShader for the geometry
    sf = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="sf_" + name)
    # Connect material to surfaceShader
    cmds.connectAttr(material + ".outColor", sf + ".surfaceShader")
    # Assign surfaceShader to objects
    cmds.sets(name, edit=True, forceElement=sf)


def assign_shaders(transform_list: [], amount, index):
    for trans in transform_list:
        clr = colorsys.hsv_to_rgb((1.0 / amount) * index, 1, 1)
        print("color of current mesh:", clr)
        create_shader(trans, clr)


# RUNNING CODE
demo_window = BatchProcessorWindow()
demo_window.show()
