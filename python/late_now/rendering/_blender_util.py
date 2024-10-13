import bpy
import os


def import_glb(file_path):
    # Store the current selection
    initial_selection = bpy.context.selected_objects

    # Clear the current selection
    bpy.ops.object.select_all(action="DESELECT")

    # Import the GLB file
    bpy.ops.import_scene.gltf(filepath=file_path)

    # Get the newly imported objects
    imported_objects = [
        obj for obj in bpy.context.selected_objects if obj not in initial_selection
    ]

    # If only one object was imported, return it directly
    if len(imported_objects) == 1:
        return imported_objects[0]

    # If multiple objects were imported, find the root (parentless) object
    root_objects = [obj for obj in imported_objects if obj.parent is None]

    # If there's only one root object, return it
    if len(root_objects) == 1:
        return root_objects[0]

    # If there are multiple root objects, create a new empty to parent them all
    if len(root_objects) > 1:
        empty = bpy.data.objects.new("GLB_Import_Root", None)
        bpy.context.scene.collection.objects.link(empty)
        for obj in root_objects:
            obj.parent = empty
        return empty

    # If no objects were imported, raise an exception
    raise ImportError("No objects were imported from the GLB file")


def import_from_blend(blend_file_path, group_name):
    if not os.path.exists(blend_file_path):
        raise ValueError(f"Error: File not found - {blend_file_path}")

    # Create a new collection to hold the imported objects
    imported_collection = bpy.data.collections.new(group_name)
    bpy.context.scene.collection.children.link(imported_collection)

    # Import all objects from the file
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    # Create an empty object to serve as a parent
    empty = bpy.data.objects.new(f"{group_name}_Parent", None)
    imported_collection.objects.link(empty)

    # Link all imported objects to the new collection and parent them to the empty
    for obj in data_to.objects:
        if obj is not None:
            imported_collection.objects.link(obj)
            obj.parent = empty

    if len(imported_collection.objects) > 1:  # >1 because we count the empty object
        return empty
    else:
        raise ValueError("no objects found in blend file")
