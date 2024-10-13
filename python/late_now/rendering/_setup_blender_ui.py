import bpy


def setup_camera_render_view():
    # Get the first 3D View area
    area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")

    # Set the view to Camera perspective
    for space in area.spaces:
        if space.type == "VIEW_3D":
            space.region_3d.view_perspective = "CAMERA"
            space.shading.type = "RENDERED"

    # Enable live update in viewport
    for scene in bpy.data.scenes:
        scene.render.use_lock_interface = (
            True  # This will update the 3D viewport in real-time
        )

    print("Camera render view setup completed successfully")


# Call the function to set up the camera render view
setup_camera_render_view()
