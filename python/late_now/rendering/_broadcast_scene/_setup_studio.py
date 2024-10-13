import bpy
import math
from late_now.rendering.constants import (
    STATIC_MESHES,
    STATIC_TEXTURES,
)
from late_now.rendering._blender_util import import_glb
from late_now.rendering._broadcast_scene._constants import FLOOR_Z


def setup_couch(scene):
    couch = import_glb(STATIC_MESHES["couch"])
    couch.scale = (0.5, 0.5, 0.5)
    couch.location = (-3, 0, FLOOR_Z)  # Updated Z coordinate
    couch.rotation_mode = "XYZ"
    couch.rotation_euler = (
        0,
        0,
        math.radians(22.5),
    )  # Rotate 22.5 degrees around Z-axis


def setup_carpet(scene):
    # Create a plane for the carpet
    bpy.ops.mesh.primitive_plane_add(size=1)
    carpet = bpy.context.active_object
    carpet.name = "Carpet"
    # Scale the carpet
    carpet.scale = (6, 3, 1)
    # Position the carpet
    carpet.location = (
        0.5,
        0,
        FLOOR_Z + 0.01,
    )  # Slightly above the floor to prevent z-fighting
    # Add material to the carpet
    mat = bpy.data.materials.new(name="CarpetMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    # Create a diffuse shader node
    node_diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
    node_diffuse.inputs[0].default_value = (
        0.545,
        0,
        0,
        1,
    )  # Dark red color (8B0000 in hex)
    # Create the output node
    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    # Link the nodes
    links = mat.node_tree.links
    links.new(node_diffuse.outputs[0], node_output.inputs[0])
    # Assign the material to the carpet
    carpet.data.materials.append(mat)


def setup_floor_plane(scene):
    bpy.ops.mesh.primitive_plane_add(size=150, location=(0, 0, FLOOR_Z))
    floor_plane = bpy.context.active_object
    mat = bpy.data.materials.new(name="Floor Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
        0.44,
        0.44,
        0.63,
        1,
    )  # Color 0x7070a0
    floor_plane.data.materials.append(mat)


def create_cube(name, scale, location):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.active_object
    cube.name = name
    cube.scale = scale
    cube.location = location
    return cube


def apply_material(obj, color=None, texture_path=None):
    material = bpy.data.materials.new(name=f"{obj.name}Material")
    material.use_nodes = True
    if color:
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    if texture_path:
        texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        texture_node.image = bpy.data.images.load(texture_path)
        material.node_tree.links.new(
            texture_node.outputs[0],
            material.node_tree.nodes["Principled BSDF"].inputs[0],
        )
    obj.data.materials.append(material)


def _create_logo_plane():
    desk_plane = bpy.context.active_object
    desk_plane.name = "DeskPlane"
    desk_plane.scale = (0.7, 0.7, 0.1)
    desk_plane.location = (0, -0.3, 0.06)
    desk_plane.rotation_euler = (math.radians(90), 0, 0)

    mat = bpy.data.materials.new(name="DeskPlaneMaterial")
    mat.use_nodes = True
    texture_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    texture_node.image = bpy.data.images.load(STATIC_TEXTURES["logo_overlay"])
    mat.node_tree.links.new(
        texture_node.outputs[0], mat.node_tree.nodes["Principled BSDF"].inputs[0]
    )
    desk_plane.data.materials.append(mat)
    return desk_plane


def setup_desk(scene):
    # Create an empty object to serve as the parent
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-0.3, -0.75, FLOOR_Z + 0.4))
    desk_parent = bpy.context.active_object
    desk_parent.name = "Desk"

    # Main desk body
    desk = create_cube("DeskBody", (1.8, -0.5, 0.9), (0, 0, 0.03))
    apply_material(desk, color=(0.247, 0.247, 0.247, 1))
    # Desk top
    desk_top = create_cube("DeskTop", (1.85, 0.75, 0.01), (0, -0.15, 0.48))
    apply_material(desk_top, color=(0.384, 0.165, 0.059, 1))
    # Desk plane (for logo overlay)
    bpy.ops.mesh.primitive_plane_add(size=1)
    desk_plane = _create_logo_plane()
    # Parent all desk parts to the empty object
    for obj in [desk, desk_top, desk_plane]:
        obj.parent = desk_parent

    return desk_parent


def setup_background_plane(scene):
    # Create the plane
    bpy.ops.mesh.primitive_plane_add(size=1)
    bg_plane = bpy.context.active_object
    bg_plane.name = "BackgroundPlane"

    # Set scale (60 units wide, 15 units tall)
    bg_plane.scale = (60, 15, 1)

    # Position the plane (adjust these values as needed)
    bg_plane.location = (0, 4, 8)

    # Rotate the plane to face the camera
    bg_plane.rotation_euler = (math.radians(90), 0, 0)

    # Create and assign material
    material = bpy.data.materials.new(name="BackgroundMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create texture node
    texture_node = nodes.new(type="ShaderNodeTexImage")
    texture_node.image = bpy.data.images.load(STATIC_TEXTURES["background"])

    # Create shader node
    shader_node = nodes.new(type="ShaderNodeBsdfPrincipled")

    # Create output node
    output_node = nodes.new(type="ShaderNodeOutputMaterial")

    # Link nodes
    links.new(texture_node.outputs["Color"], shader_node.inputs["Base Color"])
    links.new(shader_node.outputs["BSDF"], output_node.inputs["Surface"])

    # Assign material to plane
    bg_plane.data.materials.append(material)

    return bg_plane


def setup(scene, broadcast_root, params):
    setup_couch(scene)
    setup_carpet(scene)
    setup_floor_plane(scene)
    setup_desk(scene)
    setup_background_plane(scene)
