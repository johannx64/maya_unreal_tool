import unreal
import os

# Specify the folder path where .fbx files are located
folder_path = r'C:\Users\stefa\Desktop\scatter_assets\Unreal_High'

# Function to import FBX file into Unreal
def import_fbx(file_path, destination_path):
    fbx_import_ui = unreal.FbxImportUI()

    # Set import options based on your image
    fbx_import_ui.automated_import_should_detect_type = True
    fbx_import_ui.import_materials = False  # Do Not Create Material
    fbx_import_ui.import_textures = False  # Import Textures set to off
    fbx_import_ui.import_as_skeletal = False
    fbx_import_ui.import_animations = False

    # You don't need to specify 'FBXImportMaterialMethod', just turn off material creation and texture import directly.

    # Define the import task
    task = unreal.AssetImportTask()
    task.filename = file_path
    task.destination_path = destination_path
    task.destination_name = ""
    task.automated = True
    task.save = True
    task.options = fbx_import_ui

    # Import the FBX
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])


def importAssets():
    # Search for all .fbx files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".fbx"):
                file_path = os.path.join(root, file)
                destination_path = "/Game/imports2/"  # Specify your Unreal destination path here
                import_fbx(file_path, destination_path)
                print(f"Imported: {file_path}")

    print("All FBX files have been imported.")

importAssets()
