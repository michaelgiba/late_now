from late_now.plan_broadcast._types import (
    AudioFragments,
)
import os
from dataclasses import dataclass
import tempfile
import subprocess
import bpy


MOTION_GENERATED_FPS = 20

MOMASK_CODE_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "models", "momask-codes"
    )
)


def _execute_in_virtualenv(working_directory, virtualenv_path, commands):
    # Construct the command to activate the virtual environment
    activate_command = f"source {virtualenv_path}/bin/activate"

    for command in commands:
        # Combine the activation and the actual command
        full_command = f"""
        bash -c '
        {activate_command}
        {command}
        '
        """

        # Execute the command in a subprocess
        process = subprocess.Popen(full_command, shell=True, cwd=working_directory)

        # Wait for the process to complete
        process.wait()

        if process.returncode != 0:
            print(f"Error executing command: {command}")


def _generate_bvh_string(prompt: str, num_frames: int) -> str:
    with tempfile.NamedTemporaryFile() as tmp:
        _execute_in_virtualenv(
            MOMASK_CODE_ROOT,
            os.path.join(MOMASK_CODE_ROOT, ".venv"),
            [
                f"""
                python text_to_motion_custom.py \
                    --gpu_id 0 --ext exp1 --output_file {tmp.name} \
                    --text_prompt "{prompt}" --motion_length {num_frames}
                """
            ],
        )
        with open(tmp.name, "r") as f:
            content = f.read()
            return content


@dataclass
class BvhItem:
    start_frame: int
    bvh_string: str
    length_in_frames: int


def _consolidate_bvh_strings(
    start_frame_and_bvh_string: list[BvhItem],
    total_num_frames: int,
) -> BvhItem:
    # Select and delete only armatures, not everything
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            obj.select_set(True)
    bpy.ops.object.delete()

    # Sort the BvhItems by start_frame
    sorted_items = sorted(start_frame_and_bvh_string, key=lambda x: x.start_frame)

    # Import the first BVH to get the armature structure
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".bvh", delete=False
    ) as temp_file:
        temp_file.write(sorted_items[0].bvh_string)
        temp_file.flush()
        temp_file_path = temp_file.name

    # Fix axis when importing the BVH (setting Z-up for Blender's coordinate system)
    bpy.ops.import_anim.bvh(filepath=temp_file_path, axis_forward="Y", axis_up="Z")
    os.unlink(temp_file_path)

    armature = bpy.context.object
    original_rotation = armature.rotation_euler.copy()  # Store the initial rotation

    # Clear the imported animation data
    armature.animation_data_clear()

    # Create a new action for the consolidated animation
    new_action = bpy.data.actions.new(name="Consolidated Action")
    armature.animation_data_create()
    armature.animation_data.action = new_action

    current_frame = 0

    for item in sorted_items:
        # Import the current BVH
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bvh", delete=False
        ) as temp_file:
            temp_file.write(item.bvh_string)
            temp_file.flush()
            temp_file_path = temp_file.name

        # Ensure the same axis conversion is applied for each BVH import
        bpy.ops.import_anim.bvh(filepath=temp_file_path, axis_forward="Y", axis_up="Z")
        os.unlink(temp_file_path)

        imported_armature = bpy.context.object
        imported_action = imported_armature.animation_data.action

        # Rotate 180 degrees along the X-axis if the armature is upside down
        imported_armature.rotation_euler.x += (
            3.14159  # Rotate by 180 degrees along X to flip vertically
        )

        # Pad frames if there's a gap
        if item.start_frame > current_frame:
            for fcurve in new_action.fcurves:
                last_value = (
                    fcurve.evaluate(current_frame - 1) if current_frame > 0 else 0
                )
                fcurve.keyframe_points.insert(current_frame, last_value)
                fcurve.keyframe_points.insert(item.start_frame - 1, last_value)

        # Copy keyframes from the imported action to the new action
        for fcurve in imported_action.fcurves:
            new_fcurve = new_action.fcurves.find(
                fcurve.data_path, index=fcurve.array_index
            )
            if not new_fcurve:
                new_fcurve = new_action.fcurves.new(
                    fcurve.data_path, index=fcurve.array_index
                )

            for keyframe in fcurve.keyframe_points:
                new_frame = keyframe.co.x + item.start_frame
                new_fcurve.keyframe_points.insert(new_frame, keyframe.co.y)

        current_frame = item.start_frame + item.length_in_frames

        # Delete the imported armature
        bpy.data.objects.remove(imported_armature, do_unlink=True)

    # Pad the end if necessary
    if current_frame < total_num_frames:
        for fcurve in new_action.fcurves:
            last_value = fcurve.evaluate(current_frame - 1)
            fcurve.keyframe_points.insert(current_frame, last_value)
            fcurve.keyframe_points.insert(total_num_frames - 1, last_value)

    # Set the scene end frame
    bpy.context.scene.frame_end = total_num_frames

    # Ensure the armature is selected and active
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Set the armature's rotation back to its original value
    armature.rotation_euler = original_rotation

    # Export the consolidated BVH
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".bvh", delete=False
    ) as temp_file:
        temp_file_path = temp_file.name

    bpy.ops.export_anim.bvh(filepath=temp_file_path)

    # Read the exported file
    with open(temp_file_path, "r") as f:
        consolidated_bvh = f.read()

    # Clean up the temporary file
    os.unlink(temp_file_path)

    return BvhItem(
        start_frame=0, bvh_string=consolidated_bvh, length_in_frames=total_num_frames
    )


_DEFAULT_BODY_MOTION_PROMPT = "A late night show host is performing a monologue."


def generate_bvh_poses(
    speech_fragments: list[AudioFragments], num_seconds: float
) -> str:
    total_num_frames = int(num_seconds * MOTION_GENERATED_FPS)

    bvh_items = []
    for speech_fragment in speech_fragments:
        fragment_frame_start = int(
            speech_fragment.absolute_start_time_sec * MOTION_GENERATED_FPS
        )
        fragment_frame_count = int(speech_fragment.duration_sec * MOTION_GENERATED_FPS)
        bvh_single_string = _generate_bvh_string(
            speech_fragment.line_body_motion or _DEFAULT_BODY_MOTION_PROMPT,
            fragment_frame_count,
        )
        bvh_items.append(
            BvhItem(
                start_frame=fragment_frame_start,
                bvh_string=bvh_single_string,
                length_in_frames=fragment_frame_count,
            )
        )

    single_bvh = _consolidate_bvh_strings(bvh_items, total_num_frames)
    return single_bvh.bvh_string
