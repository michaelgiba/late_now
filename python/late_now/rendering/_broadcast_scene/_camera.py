import bpy
import math
from mathutils import Vector
from late_now.rendering._broadcast_scene._constants import FLOOR_Z, ANCHOR_X
from late_now.rendering._core import Updater


# Helper function to set the camera's "look at" orientation
def look_at(camera_obj, target_vector):
    """
    Points a camera object in Blender towards a specific target vector.

    Args:
        camera_obj (bpy.types.Object): The camera object to adjust.
        target_vector (mathutils.Vector): The 3D vector representing the target point.
    """

    # Ensure the camera object is indeed a camera
    if camera_obj.type != "CAMERA":
        raise TypeError("Object provided is not a camera.")

    # Get the camera's location
    camera_location = camera_obj.location

    # Calculate the direction vector from the camera to the target
    direction = target_vector - camera_location

    # Point the camera in the calculated direction
    rot_quat = direction.to_track_quat(
        "-Z", "Y"
    )  # '-Z' is the camera's viewing direction, 'Y' is the up axis
    camera_obj.rotation_euler = rot_quat.to_euler()


def setup_camera(
    scene, name, location, fov, target, orthographic=False, ortho_scale=10
):
    """
    Creates a new camera with specified parameters and adds it to the scene.

    Args:
        scene: The Blender scene where the camera will be added.
        name (str): Name of the camera object.
        location (tuple): The location of the camera (x, y, z).
        fov (float): Field of view in degrees.
        target (tuple): The target point for the camera to look at (x, y, z).
        orthographic (bool): Whether the camera should be orthographic or perspective.
        ortho_scale (float): The scale of the orthographic camera.
    """
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.angle = math.radians(fov)  # Convert FOV from degrees to radians
    cam_data.type = "ORTHO" if orthographic else "PERSP"
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    scene.collection.objects.link(cam_obj)

    # Set the camera position and look at target
    cam_obj.location = Vector(location)
    look_at(cam_obj, Vector(target))

    return cam_obj


class CameraUpdater(Updater):
    def __init__(self, camera):
        self.camera = camera

    def update(self, frame):
        # Calculate the sway motion
        sway_amount = (
            math.sin(frame * 0.1) * 2
        )  # Adjust the amplitude and speed as desired

        # Update the camera's position and orientation based on the frame
        self.camera.location = (frame + sway_amount, 0, 0)
        look_at(self.camera, Vector((0, 0, 0)))

    def set_active(self):
        bpy.context.scene.camera = self.camera


def setup_cameras(scene):
    """
    Sets up multiple cameras in the scene with adjusted coordinates for Blender.
    """
    # Camera Main (Adjusted for Blender: swap Y and Z, and flip Z)
    cam_main = setup_camera(
        scene,
        name="Camera Main",
        location=(ANCHOR_X - 0.3, -10, FLOOR_Z + 1.35),  # Swap Y and Z, flip Z
        fov=15,
        target=(ANCHOR_X - 0.3, 0, FLOOR_Z + 1.35),  # Adjusted accordingly
        orthographic=True,
        ortho_scale=2.5,
    )

    # Camera Persona (Adjusted for Blender)
    cam_persona = setup_camera(
        scene,
        name="Camera Persona",
        location=(ANCHOR_X, -4, FLOOR_Z + 1.35),  # Swap Y and Z, flip Z
        fov=25,
        target=(ANCHOR_X, 0, FLOOR_Z + 1.35),  # Adjusted accordingly
    )

    # Camera Side Left (Adjusted for Blender)
    cam_side_left = setup_camera(
        scene,
        name="Camera Side Left",
        location=(ANCHOR_X - 5, -4, FLOOR_Z + 3),  # Swap Y and Z, flip Z
        fov=90,
        target=(0, 0, FLOOR_Z + 1.35),  # Adjusted accordingly
    )

    # Camera Side Right (Adjusted for Blender)
    cam_side_right = setup_camera(
        scene,
        name="Camera Side Right",
        location=(ANCHOR_X + 2, -5, FLOOR_Z + 2),  # Swap Y and Z, flip Z
        fov=90,
        target=(0, 0, FLOOR_Z + 1.35),  # Adjusted accordingly
    )

    camera_updates = {
        "main": CameraUpdater(cam_main),
        "persona": CameraUpdater(cam_persona),
        "side_left": CameraUpdater(cam_side_left),
        "side_right": CameraUpdater(cam_side_right),
    }

    camera_updates["main"].set_active()

    return camera_updates
