import bpy
import os
import json
from late_now.rendering.constants import STATIC_MESHES
import tempfile
from late_now.rendering._blender_util import import_from_blend
from late_now.rendering._broadcast_scene._constants import FLOOR_Z
from late_now.rendering._broadcast_scene.animations import face, rig
from late_now.rendering._core import Updater, CompositeUpdater
import sys


def _face_updater(anchor, animation_data):
    shape_key_name_to_obj = face.load_targets(anchor)
    frames_packed = animation_data["blendshape_data"]["blendshape_frames"]
    key_name_to_packed_index = animation_data["blendshape_data"][
        "blendshape_name_to_index"
    ]

    def _get_dict_data_for_frame(index):
        try:
            packed_frame_data = frames_packed[index]["values"]
        except IndexError:
            print(f"Index {index} is out of range for frames_packed")
            sys.exit(1)
        return {
            key_name: packed_frame_data[packed_index]
            for key_name in key_name_to_packed_index
            for packed_index in [key_name_to_packed_index[key_name]]
        }

    class FaceUpdater(Updater):
        def update(self, frame_index: int):
            face.set_shape_key_values(
                shape_key_name_to_obj, _get_dict_data_for_frame(frame_index)
            )
            bpy.context.scene.frame_set(frame_index)
            bpy.context.view_layer.update()

    return FaceUpdater()


def _rig_updater(anchor, animation_data):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".bvh") as bvh_file:
        bvh_file.write(animation_data["bvh_data_strings"][0])
        bvh_file.seek(0)  # Move the file pointer to the start of the file
        rig.perform_animation_remapping(anchor, bvh_file.name)
    # rig.perform_animation_remapping(anchor, STATIC_ANIMATIONS["slapping"])

    class RigUpdater(Updater):
        def update(self, frame_index: int):
            rig.update_frame(frame_index)

    return RigUpdater()


def _optimze_anchor(anchor):
    names_to_decimate = [
        "down_hair.001",
        "upper_hair.001",
        "pants1",
    ]  # Adjust this list as needed

    def _decimate_specific_children(obj, names, ratio=0.1):
        if obj.type == "MESH" and obj.name in names:
            # Add Decimate modifier
            decimate_modifier = obj.modifiers.new(name="Decimate", type="DECIMATE")
            if decimate_modifier is not None:
                decimate_modifier.ratio = ratio
                print(f"Added Decimate modifier to '{obj.name}' with ratio {ratio}")

                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier="Decimate")

        for child in obj.children:
            _decimate_specific_children(child, names, ratio)

    _decimate_specific_children(anchor, names_to_decimate)


def setup(scene, broadcast_root, params):
    walter_animation_path = params["character_to_animation"]["walter"]

    with open(os.path.join(broadcast_root, walter_animation_path)) as f:
        walter_animation = json.load(f)

    anchor = import_from_blend(STATIC_MESHES["walter"], "walter")

    if anchor is None:
        raise ValueError("Failed to import the Walter mesh")

    anchor.scale = (0.17, 0.17, 0.17)
    anchor.location = (0, 0, FLOOR_Z)  # Adjusted Z coordinate
    _optimze_anchor(anchor)

    return CompositeUpdater(
        _face_updater(anchor, walter_animation),
        _rig_updater(anchor, walter_animation),
    )
