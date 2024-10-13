import bpy

# import math
# import random
# from late_now.rendering.constants import STATIC_MESHES
# from late_now.rendering._blender_util import import_glb
# from late_now.rendering._broadcast_scene._constants import FLOOR_Z


# TODO: Re-enable audience
def setup_audience(scene):
    # audience_group = _create_collection(scene, "Audience")
    # audience_root = _create_audience_root(audience_group, "AudienceRoot", (0, 7, FLOOR_Z))
    # audience_root.rotation_euler = (0, math.pi, 0)

    # # Import the audience GLB
    # original_model = import_glb(STATIC_MESHES["audience"])
    # original_model.scale = (0.5, 0.5, 0.2)

    # # Get animations
    # # animations = original_model.animation_data.nla_tracks

    # for i in range(200):
    #     model = original_model.copy()
    #     model.data = original_model.data.copy()
    #     model.animation_data_create()

    #     # Position the model randomly
    #     z_pos = (random.random() - 0.5) * 5
    #     model.location = (
    #         (random.random() - 0.5) * 12,
    #         z_pos,
    #         0.2 - z_pos * 0.2
    #     )

    #     # Set up animation
    #     potential_actions = ['HumanArmature|Man_Clapping', 'HumanArmature|Man_Standing']
    #     target_action = random.choice(potential_actions)

    #     # for track in animations:
    #     #     if track.name == target_action:
    #     #         new_track = model.animation_data.nla_tracks.new()
    #     #         new_track.name = track.name
    #     #         for strip in track.strips:
    #     #             new_strip = new_track.strips.new(strip.name, strip.frame_start, strip.action)
    #     #             new_strip.use_auto_blend = True
    #     #             new_strip.blend_type = 'REPLACE'
    #     #             new_strip.use_sync_length = True
    #     #             new_strip.repeat = 1000  # Set to a high number for looping

    #     audience_root.children.link(model)

    # # Remove the original model
    # bpy.data.objects.remove(original_model, do_unlink=True)
    pass


def _create_collection(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def _create_audience_root(group, name, location):
    root = bpy.data.objects.new(name, None)
    root.location = location
    group.objects.link(root)
    return root
