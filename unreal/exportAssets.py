import unreal
import os
assets_path = ".\\assets"

# Specify the folder path where .fbx files are located
folder_path = r'C:\\Users\\stefa\\Pictures\\unrealscript\\core\\maya\\'

def exportSelectedMeshes():
    """
    Export selected static meshes to FBX files.
    """
    # Get selected assets from content browser
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    # Check if any assets are selected
    if not selectedAssets:
        unreal.log("No assets selected for export!")
        return
    
    unreal.log("Starting export of selected static meshes...")
    
    for selectedAsset in selectedAssets:
        if isinstance(selectedAsset, unreal.StaticMesh):
            assetName = selectedAsset.get_name()
            unreal.log("Exporting mesh: {}".format(assetName))
            
            # Create asset export task
            exportTask = unreal.AssetExportTask()
            exportTask.automated = True
            exportTask.object = selectedAsset
            exportTask.prompt = False
            
            # Set the filename and export options
            exportTask.filename = assets_path + "\\" + assetName + '.fbx'
            exportTask.options = unreal.FbxExportOption()
            fbxExporter = unreal.StaticMeshExporterFBX()
            exportTask.exporter = fbxExporter
            
            # Run export task
            result = fbxExporter.run_asset_export_task(exportTask)
            if result:
                unreal.log("Successfully exported Static Mesh: {}".format(assetName))
            else:
                unreal.log_error("Failed to export Static Mesh: {}".format(assetName))
        else:
            unreal.log_warning("Asset type not supported for export: {}".format(selectedAsset.get_name()))
    
    unreal.log("Mesh export process completed.")

 # Function to import FBX file into Unreal

def import_fbx(file_path, destination_path):
    fbx_import_ui = unreal.FbxImportUI()
    fbx_import_ui.automated_import_should_detect_type = True
    fbx_import_ui.import_materials = True
    fbx_import_ui.import_textures = True
    fbx_import_ui.import_as_skeletal = False
    fbx_import_ui.import_animations = False
    
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

