import bpy
from functools import cache


def find_armature_name(input_mesh):
    armature_name = None

    # Iterate through the children of the input mesh to find the armature
    for child in input_mesh.children:
        if child.type == "ARMATURE":
            armature_name = child.name
            break

    return armature_name


@cache
def _load_bvh_data(bvh_data_path: str):
    # Import BVH file
    bpy.ops.import_anim.bvh(filepath=bvh_data_path)

    # Get the imported armature
    bvh_armature = next(
        obj for obj in bpy.context.selected_objects if obj.type == "ARMATURE"
    )

    bvh_armature.name = bvh_data_path

    # Make the armature very small and transparent
    bvh_armature.scale = (0.001, 0.001, 0.001)  # Adjust the scale as needed
    for bone in bvh_armature.data.bones:
        bone.hide_select = True  # Prevent accidental selection

    # Set the display type to 'Wire' and reduce opacity
    bvh_armature.display_type = "WIRE"
    bvh_armature.show_in_front = True

    # Set the action to cyclic to allow looping
    if bvh_armature.animation_data and bvh_armature.animation_data.action:
        action = bvh_armature.animation_data.action
        action.fcurves.update()  # Ensure F-curves are up-to-date
        for fcurve in action.fcurves:
            for modifier in fcurve.modifiers:
                if modifier.type == "CYCLES":
                    break
            else:
                # Add a Cycles modifier to loop the animation
                fcurve.modifiers.new(type="CYCLES")

    # Calculate the animation scale factor
    scale_factor = 30 / 20  # SCENE_FPS / BVH_FPS

    # Scale keyframes
    for fcurve in bvh_armature.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.co.x *= scale_factor
            kf.handle_left.x *= scale_factor
            kf.handle_right.x *= scale_factor

    # Set interpolation to Bezier for smooth interpolation
    for fcurve in bvh_armature.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = "BEZIER"

    return bvh_armature


def perform_animation_remapping(anchor, bvh_data_path):
    bvh_armature = _load_bvh_data(bvh_data_path)

    bpy.context.scene.source_rig = bvh_armature.name
    bpy.context.scene.target_rig = find_armature_name(anchor)

    bpy.ops.arp.auto_scale()
    bpy.ops.arp.build_bones_list()
    bpy.ops.arp.retarget_bind_only()


def update_frame(frame_index: int):
    bpy.context.scene.frame_set(frame_index)
    bpy.context.view_layer.update()
