import maya.cmds as cmds

# Constants
WINDOW_WIDTH = 300
COLUMN_COUNT = 4
COLUMN_WIDTH = WINDOW_WIDTH / COLUMN_COUNT
GRID_HEIGHT = 20

def create_grid_layout(root):
    # Create the main layout
    main_layout = cmds.columnLayout(p=root, adj=True)

    # Create a frame layout without borderStyle
    frame = cmds.frameLayout(p=main_layout, label="Mesh Groups", width=WINDOW_WIDTH)
    
    # Create a column layout inside the frame layout for better resizing
    column = cmds.columnLayout(p=frame, adjustableColumn=True)

    # Create the grid layout inside the column layout
    grid_layout = cmds.gridLayout(p=column, numberOfColumns=COLUMN_COUNT, cellWidthHeight=(COLUMN_WIDTH, GRID_HEIGHT))
    
    # Column headers
    headers = ["Selected", "Moss", "Plants", "Path"]
    for header in headers:
        cmds.text(label=header, align='center', parent=grid_layout)

    # Example data, with all checkboxes defaulting to True
    items = [
        {"selected": True, "moss": True, "plants": True, "path": "Path1"},
        {"selected": True, "moss": True, "plants": True, "path": "Path2"},
        {"selected": True, "moss": True, "plants": True, "path": "Path3"}
    ]

    # Add data rows
    for item in items:
        # Add checkbox for the 'Selected' column
        cmds.checkBox(label="", value=item["selected"], parent=grid_layout)

        # Add checkboxes for 'Moss' and 'Plants' columns
        cmds.checkBox(label="", value=item["moss"], parent=grid_layout)
        cmds.checkBox(label="", value=item["plants"], parent=grid_layout)

        # Add text field for 'Path' column
        cmds.text(label=item["path"], parent=grid_layout)

def create_ui():
    # Create a new window
    if cmds.window("myWindow", exists=True):
        cmds.deleteUI("myWindow", window=True)

    window = cmds.window("myWindow", title="Mesh Groups UI", widthHeight=(WINDOW_WIDTH, 200), sizeable=True)

    cmds.columnLayout(adjustableColumn=True)

    create_grid_layout("myWindow")

    # Show the window
    cmds.showWindow(window)

create_ui()
