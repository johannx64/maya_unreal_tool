import unreal

assets_path = ".\\assets"

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

def importAssets():
    """
    Import an FBX asset into the project with specific material import options,
    print the result, and ensure automatic import without any dialogs.
    """
    # List of FBX files to import
    fileNames = [
        r'C:\Users\stefa\Pictures\unrealscript\core\maya\exported_bone.fbx',
    ]
    
    # Destination path where the assets will be imported
    destination_path = r'/Game/imports2/'
    
    # Reference to Asset Tools for importing
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()

    for fileName in fileNames:
        # Set up FBX import options
        fbx_import_options = unreal.FbxImportUI()
        fbx_import_options.automated = True
        fbx_import_options.import_materials = True
        fbx_import_options.material_search_location = unreal.MaterialSearchLocation.ALL_ASSETS
        fbx_import_options.import_as_skeletal = False  # Assuming it's a static mesh
        
        # Set material import method to "Do not create material"
        fbx_import_options.static_mesh_import_data.import_materials = False
        
        # Perform the import
        imported_assets = unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated_with_import_options(
            fileNames, destination_path, fbx_import_options
        )
        
        if imported_assets:
            for asset in imported_assets:
                unreal.log("Successfully imported: {}".format(asset.get_name()))
        else:
            unreal.log_error("Failed to import assets.")