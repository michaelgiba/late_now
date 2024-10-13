import bpy
import math


def setup_lights(scene):
    # Clear existing lights
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_by_type(type="LIGHT")
    bpy.ops.object.delete()

    # Main Key Light (Warm with a golden tinge)
    key_light = bpy.data.lights.new(name="Key Light", type="AREA")
    key_light.energy = 700
    key_light.color = (1, 0.96, 0.87)  # Warm golden white
    key_light_obj = bpy.data.objects.new(name="Key Light", object_data=key_light)
    bpy.context.collection.objects.link(key_light_obj)
    key_light_obj.location = (3, -4, 4)
    key_light_obj.rotation_euler = (math.radians(60), 0, math.radians(-45))
    key_light.shape = "RECTANGLE"
    key_light.size = 2
    key_light.size_y = 1

    # Fill Light (Soft warm with a touch of peach)
    fill_light = bpy.data.lights.new(name="Fill Light", type="AREA")
    fill_light.energy = 200
    fill_light.color = (1, 0.95, 0.91)  # Soft peachy white
    fill_light_obj = bpy.data.objects.new(name="Fill Light", object_data=fill_light)
    bpy.context.collection.objects.link(fill_light_obj)
    fill_light_obj.location = (-3, -4, 3)
    fill_light_obj.rotation_euler = (math.radians(60), 0, math.radians(45))
    fill_light.shape = "RECTANGLE"
    fill_light.size = 2
    fill_light.size_y = 1

    # Backlight (Neutral with a slight lavender tint)
    back_light = bpy.data.lights.new(name="Back Light", type="AREA")
    back_light.energy = 250
    back_light.color = (0.98, 0.96, 1)  # Slight lavender tint
    back_light_obj = bpy.data.objects.new(name="Back Light", object_data=back_light)
    bpy.context.collection.objects.link(back_light_obj)
    back_light_obj.location = (0, 2, 4)
    back_light_obj.rotation_euler = (math.radians(-60), 0, 0)
    back_light.shape = "RECTANGLE"
    back_light.size = 2
    back_light.size_y = 0.5

    # Ambient Light (Warm glow)
    ambient_light = bpy.data.lights.new(name="Ambient Light", type="POINT")
    ambient_light.energy = 45
    ambient_light.color = (1, 0.9, 0.8)  # Warm ambient glow
    ambient_light_obj = bpy.data.objects.new(
        name="Ambient Light", object_data=ambient_light
    )
    bpy.context.collection.objects.link(ambient_light_obj)
    ambient_light_obj.location = (0, 0, 5)

    # Stage Lights (Subtle color accents)
    def create_stage_light(name, color, location, energy=250):
        light = bpy.data.lights.new(name=name, type="SPOT")
        light.energy = energy
        light.color = color
        light_obj = bpy.data.objects.new(name=name, object_data=light)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = location
        light_obj.rotation_euler = (math.radians(75), 0, 0)  # Slightly angled
        light.spot_size = math.radians(50)  # Wider, softer beam
        light.spot_blend = 0.5  # Very soft edges
        return light_obj

    create_stage_light("Stage Light 1", (1, 0.5, 0.3), (-4, 1, 5))  # Warm orange
    create_stage_light("Stage Light 2", (0.3, 0.6, 1), (4, 1, 5))  # Soft blue
    create_stage_light("Stage Light 3", (0.5, 1, 0.5), (0, -4, 5))  # Soft green

    # Rim lights for subtle color accents
    def create_rim_light(name, color, location, energy=250):
        light = bpy.data.lights.new(name=name, type="AREA")
        light.energy = energy
        light.color = color
        light_obj = bpy.data.objects.new(name=name, object_data=light)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = location
        light_obj.rotation_euler = (0, math.radians(90), 0)  # Point towards the center
        light.shape = "RECTANGLE"
        light.size = 1
        light.size_y = 0.5
        return light_obj

    create_rim_light("Rim Light 1", (1, 0.8, 0.6), (-5, 0, 2))  # Warm orange rim
    create_rim_light("Rim Light 2", (0.6, 0.9, 1), (5, 0, 2))  # Cool blue rim

    # Set up world background
    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes.clear()
    bg = world.node_tree.nodes.new(type="ShaderNodeBackground")
    bg.inputs["Color"].default_value = (
        0.1,
        0.11,
        0.13,
        1,
    )  # Slightly warmer dark background
    output = world.node_tree.nodes.new(type="ShaderNodeOutputWorld")
    world.node_tree.links.new(bg.outputs["Background"], output.inputs["Surface"])

    print("Warm, colorful studio lighting setup completed successfully")
