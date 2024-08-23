import maya.cmds as cmds
import os

# Constants
WINDOW_WIDTH = 700
GRID_HEIGHT = 20

# Global variables to hold the list of FBX files and available assets
fbx_files = []
available_assets = []

def browse_folder():
    """Browse for a folder containing .fbx files."""
    folder = cmds.fileDialog2(fileMode=3, caption="Select Folder")[0]
    if folder:
        populate_fbx_list(folder)

def populate_fbx_list(folder):
    """Populate the list with .fbx files from the selected folder."""
    global fbx_files
    fbx_files = [f for f in os.listdir(folder) if f.endswith('.fbx')]
    refresh_import_list()
    refresh_export_list()

def browse_assets_folder():
    """Browse for a folder containing assets to scatter/age."""
    folder = cmds.fileDialog2(fileMode=3, caption="Select Assets Folder")[0]
    if folder:
        populate_assets_list(folder)

def populate_assets_list(folder):
    """Populate the list with assets from the selected folder."""
    global available_assets
    available_assets = [f for f in os.listdir(folder) if f.endswith('.fbx')]
    refresh_assets_list()

def refresh_import_list():
    """Refresh the import list UI."""
    cmds.textScrollList('importList', edit=True, removeAll=True)
    for fbx_file in fbx_files:
        cmds.textScrollList('importList', edit=True, append=fbx_file)

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

def remove_from_export_list(fbx, row):
    """Remove an item from the export list."""
    global fbx_files
    fbx_files = [item for item in fbx_files if item != fbx]
    cmds.deleteUI(row, layout=True)
    refresh_import_list()

def create_import_ui(root):
    """Create the import UI section."""
    frame = cmds.frameLayout(p=root, label="FBX Importer", width=WINDOW_WIDTH)
    column = cmds.columnLayout(p=frame, adjustableColumn=True)
    cmds.button(label="Browse Folder", parent=column, command=lambda _: browse_folder())
    cmds.textScrollList('importList', parent=column, height=100)
    cmds.button(label="Remove Selected", parent=column, command=lambda _: remove_selected_import())

def create_assets_ui(root):
    """Create the assets selection UI section."""
    frame = cmds.frameLayout(p=root, label="Scatter/Aging Assets", width=WINDOW_WIDTH)
    column = cmds.columnLayout(p=frame, adjustableColumn=True)
    cmds.button(label="Select Assets Folder", parent=column, command=lambda _: browse_assets_folder())
    cmds.textScrollList('assetsList', parent=column, height=120)

def create_export_ui():
    """Create the export UI section."""
    if cmds.scrollLayout('exportScroll', exists=True):
        cmds.deleteUI('exportScroll', layout=True)

    export_scroll = cmds.scrollLayout('exportScroll', parent='mainLayout', width=WINDOW_WIDTH, height=300)
    export_column = cmds.columnLayout(p=export_scroll, adjustableColumn=True)
    
    # Column headers
    cmds.rowLayout(numberOfColumns=6, adjustableColumn=3, columnWidth6=[50, 50, 250, 200, 100, 100], parent=export_column)
    cmds.text(label="Moss", align='center')
    cmds.text(label="Plants", align='center')
    cmds.text(label="Name", align='center')
    cmds.text(label="Available Assets", align='center')
    cmds.text(label="Select All", align='center')
    cmds.text(label="Remove", align='center')

    for fbx_file in fbx_files:
        row = cmds.rowLayout(numberOfColumns=6, adjustableColumn=3, columnWidth6=[50, 50, 250, 200, 100, 100], parent=export_column)
        cmds.checkBox(label="", value=True, parent=row)
        cmds.checkBox(label="", value=True, parent=row)

        # Display the name of the FBX file
        cmds.text(label=fbx_file, align='left', parent=row)

        # Create a dropdown menu for available assets
        asset_list = cmds.textScrollList(allowMultiSelection=True, height=60, append=available_assets, parent=row)

        # "Select All" button for the asset list within the row
        cmds.button(label="Select All", parent=row, command=lambda x=asset_list: select_all_items(x))
        
        # "Remove" button for the row
        cmds.button(label="Remove", parent=row, command=lambda x=fbx_file, y=row: remove_from_export_list(x, y))

def refresh_export_list():
    """Refresh the export list UI."""
    create_export_ui()

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

    cmds.showWindow(window)

create_ui()
