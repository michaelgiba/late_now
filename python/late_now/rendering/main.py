import subprocess
import os
import pkg_resources

BLENDER_EXECUTABLE = os.environ.get("BLENDER_EXECUTABLE")
if not BLENDER_EXECUTABLE:
    raise ValueError("BLENDER_EXECUTABLE environment variable is not set")

late_now_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_ROOT = f"{late_now_ROOT}/late_now/rendering/output/"
BROADCAST_ROOT = pkg_resources.resource_filename(__name__, "assets/broadcasts/main/")


def render_blender(broadcast_root: str, output_root: str, show_ui=False):
    """
    Launch Blender and run the `start_scene` function defined in `blender_script.py`.

    :param show_ui: If True, Blender will show its UI; otherwise, it runs in headless mode.
    """
    script_path = "late_now.rendering._entrypoint"
    # Python expression to modify sys.path, import the script, and call start_scene
    python_expr = (
        f"import sys; sys.path.append('{late_now_ROOT}'); "
        f"import {script_path}; {script_path}.start_scene('{broadcast_root}', '{output_root}'); "
        # f"from late_now.rendering import _setup_blender_ui; _setup_blender_ui.setup_camera_render_view()"
    )

    # Blender command
    blender_cmd = [
        BLENDER_EXECUTABLE,
        (
            "--background" if not show_ui else ""
        ),  # Run in background mode if show_ui is False
        "--python-expr",
        python_expr,  # Execute the Python expression inside Blender
    ]

    # Filter out empty strings if show_ui is True
    blender_cmd = [arg for arg in blender_cmd if arg]

    try:
        # Launch Blender with the specified command
        print(f"Running Blender with command: {' '.join(blender_cmd)}")
        subprocess.run(blender_cmd, check=True)
        print("Blender function executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Blender: {e}")


def composite_blender(composite_root: str, output_video_path: str):
    """
    Launch Blender and run the `start_scene` function defined in `blender_script.py`.

    :param show_ui: If True, Blender will show its UI; otherwise, it runs in headless mode.
    """
    script_path = "late_now.rendering._entrypoint_compositing"
    # Python expression to modify sys.path, import the script, and call start_scene
    python_expr = (
        f"import sys; sys.path.append('{late_now_ROOT}'); "
        f"import {script_path}; {script_path}.main(composite_root='{composite_root}', output_video_path='{output_video_path}'); "
        # f"from late_now.rendering import _setup_blender_ui; _setup_blender_ui.setup_camera_render_view()"
    )

    # Blender command
    blender_cmd = [
        BLENDER_EXECUTABLE,
        "--python-expr",
        python_expr,  # Execute the Python expression inside Blender
    ]

    # Filter out empty strings if show_ui is True
    blender_cmd = [arg for arg in blender_cmd if arg]

    try:
        # Launch Blender with the specified command
        print(f"Running Blender with command: {' '.join(blender_cmd)}")
        subprocess.run(blender_cmd, check=True)
        print("Blender function executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Blender: {e}")
