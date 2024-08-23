import unreal
import os

assets_path = r"C:\Users\stefa\Desktop\scatter_assets\Unreal_High"

# Specify the root folder where the search for Static Meshes should start
folder_path = r'/Game/Megascans/3D_Assets'  # Change this to your desired root folder in Unreal

def export_all_meshes_in_folder(root_folder):
    """
    Recursively find and export all Static Meshes in the given folder and its subfolders.
    """
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    # Search for all assets in the folder and subfolders
    asset_filter = unreal.ARFilter(
        package_paths=[root_folder],
        recursive_paths=True,
        class_names=["StaticMesh"]
    )

    found_assets = asset_registry.get_assets(asset_filter)

    if not found_assets:
        unreal.log("No assets found for export in the specified folder.")
        return

    unreal.log("Starting export of Static Meshes from folder: {}".format(root_folder))

    for asset_data in found_assets:
        asset = asset_data.get_asset()

        if isinstance(asset, unreal.StaticMesh):
            asset_name = asset.get_name()
            unreal.log("Exporting mesh: {}".format(asset_name))

            # Create asset export task
            export_task = unreal.AssetExportTask()
            export_task.automated = True
            export_task.object = asset
            export_task.prompt = False

            # Set the filename
            export_task.filename = os.path.join(assets_path, asset_name + '.fbx')

            # Create Fbx export options and set the required options
            export_options = unreal.FbxExportOption()
            export_options.export_source_mesh = True  # Export only the highest LOD (source mesh)
            export_options.level_of_detail = False    # Disable exporting other LODs
            export_task.options = export_options

            # Create the FBX exporter
            fbx_exporter = unreal.StaticMeshExporterFBX()
            export_task.exporter = fbx_exporter

            # Run the export task
            result = fbx_exporter.run_asset_export_task(export_task)
            if result:
                unreal.log("Successfully exported Static Mesh: {}".format(asset_name))
            else:
                unreal.log_error("Failed to export Static Mesh: {}".format(asset_name))

        else:
            unreal.log_warning("Asset type not supported for export: {}".format(asset_data.asset_name))

    unreal.log("Mesh export process completed.")

# Call the function to export all meshes in the folder (including subfolders)
export_all_meshes_in_folder(folder_path)