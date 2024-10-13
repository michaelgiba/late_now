import bpy
import math
from late_now.rendering.constants import STATIC_MESHES
from late_now.rendering._blender_util import import_glb
from late_now.rendering._broadcast_scene._constants import FLOOR_Z

BAND_POSITION = (-3, 2.1, FLOOR_Z)


def setup_band(scene):
    band_group = _create_collection(scene, "Band")
    band_root = _create_band_root(band_group, "BandRoot", BAND_POSITION)

    _create_carpet(band_root, scene)

    _create_musician(
        band_root,
        "SaxMan",
        STATIC_MESHES["bandMember"],
        (1.25, -0.7, 0.65),
        0.15,
        (0, 0, math.radians(180)),
    )
    _create_instrument(band_root, "Sax", STATIC_MESHES["sax"], (1.25, -1, 0.2), 0.04)

    _create_musician(
        band_root,
        "DrumMan",
        STATIC_MESHES["bandMember"],
        (0, 1, 0.65),
        0.15,
        (0, 0, math.radians(180)),
    )
    _create_instrument(band_root, "Drum", STATIC_MESHES["drum"], (0, 0.5, 0.45), 1)

    _create_musician(
        band_root,
        "KeysMan",
        STATIC_MESHES["bandMember"],
        (-1, 0, 0.65),
        0.15,
        (0, 0, math.radians(90)),
    )
    _create_instrument(
        band_root,
        "Piano",
        STATIC_MESHES["piano"],
        (-1.8, 0, 0),
        0.08,
        (0, 0, math.radians(-45)),
    )


def _create_collection(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def _create_band_root(group, name, location):
    root = bpy.data.objects.new(name, None)
    root.location = location
    root.rotation_euler = (0, 0, math.pi / 8)

    group.objects.link(root)
    return root


def _create_musician(parent, name, glb_path, location, scale, rotation=(0, 0, 0)):
    musician = _import_and_setup(glb_path, name, location, scale, rotation)
    musician.parent = parent
    musician.rotation_mode = "XYZ"
    musician.rotation_euler = rotation
    return musician


def _create_instrument(parent, name, glb_path, location, scale, rotation=(0, 0, 0)):
    instrument = _import_and_setup(glb_path, name, location, scale, rotation)
    instrument.parent = parent
    return instrument


def _import_and_setup(glb_path, name, location, scale, rotation):
    obj = import_glb(glb_path)
    obj.name = name
    obj.location = location
    obj.scale = (scale, scale, scale)
    obj.rotation_euler = rotation
    return obj


def _create_carpet(parent, scene):
    bpy.ops.mesh.primitive_cube_add(size=1)
    carpet = bpy.context.active_object
    carpet.name = "BandCarpet"
    carpet.scale = (5, 3, 0.1)

    mat = bpy.data.materials.new(name="CarpetMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_principled.inputs["Base Color"].default_value = (
        0.545,
        0,
        0,
        1,
    )  # Dark red color (8B0000)
    mat.node_tree.links.new(
        node_principled.outputs["BSDF"], node_output.inputs["Surface"]
    )
    carpet.data.materials.append(mat)

    carpet.parent = parent
    if carpet.name in scene.collection.objects:
        scene.collection.objects.unlink(carpet)
