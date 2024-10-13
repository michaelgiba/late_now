import bpy
from late_now.rendering._broadcast_scene import (
    _setup_studio,
    _lighting,
    _camera,
    _setup_anchor,
)
from late_now.rendering._core import Updater
from late_now.rendering.constants import FRAME_TIME_SEC


class CameraCutUpdater(Updater):
    def __init__(self, *, camera_cut_params, camera_updaters):
        total_duration_sec = 0.0
        camera_cuts_and_start_frame = []
        for camera_cut_info in camera_cut_params:
            cut_name = camera_cut_info["camera"]
            camera_cuts_and_start_frame.append(
                (int(total_duration_sec / FRAME_TIME_SEC), cut_name)
            )
            total_duration_sec += camera_cut_info["duration_sec"]

        self._cut_frame_index_to_name = dict(camera_cuts_and_start_frame)
        self.camera_updaters = camera_updaters

    def update(self, frame):
        if cut_name := self._cut_frame_index_to_name.get(frame):
            if cut_name in ["fly_in"]:
                return
            if updater := self.camera_updaters[cut_name]:
                updater.set_active()


def broadcast_scene(broadcast_root, params):
    scene = bpy.context.scene
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    cameras = _camera.setup_cameras(scene)

    camera_cut_params = params["camera_cuts"]

    camera_cut_updater = CameraCutUpdater(
        camera_cut_params=camera_cut_params, camera_updaters=cameras
    )

    _lighting.setup_lights(scene)
    # _setup_band.setup_band(scene)
    _setup_studio.setup(scene, broadcast_root, params)
    # _setup_audience.setup_audience(scene)
    anchor_updater = _setup_anchor.setup(scene, broadcast_root, params)

    def update_frame(frame):
        bpy.context.scene.frame_set(frame)
        anchor_updater.update(frame)
        camera_cut_updater.update(frame)

    return update_frame
