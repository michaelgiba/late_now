import bpy
import json
import os
import sys
from functools import cache
from late_now.rendering.intro import intro_scene
from late_now.rendering._broadcast_scene import broadcast_scene
from late_now.rendering.constants import RENDER_FPS, FRAME_TIME_SEC, DEBUG


@cache
def _load_broadcast_index(path):
    with open(os.path.join(path, "index.json")) as f:
        return json.load(f)


# Map sequence types to functions
SEQUENCE_TYPE_TO_FUNCTION = {
    "intro": intro_scene,
    "broadcast": broadcast_scene,
}

_FAST_RENDER = False


def setup_blender_scene():
    # Basic scene setup
    bpy.context.scene.render.fps = RENDER_FPS
    bpy.context.scene.render.resolution_x = 376
    bpy.context.scene.render.resolution_y = 812
    bpy.context.scene.render.film_transparent = True

    # Render engine setup
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"

    if _FAST_RENDER:
        # EEVEE settings for fast rendering
        bpy.context.scene.eevee.taa_render_samples = 4
        bpy.context.scene.eevee.taa_samples = 2
        bpy.context.scene.eevee.use_bloom = False
        bpy.context.scene.eevee.use_ssr = False
        bpy.context.scene.eevee.shadow_cube_size = "128"
        bpy.context.scene.eevee.shadow_cascade_size = "128"
        bpy.context.scene.eevee.use_gtao = False
        bpy.context.scene.eevee.use_ssr_refraction = False

        # Lighting and shadows settings for speed
        bpy.context.scene.eevee.use_soft_shadows = False
        bpy.context.scene.eevee.gi_diffuse_bounces = 0

        # Performance settings
        bpy.context.preferences.system.use_gpu_subdivision = False
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision_render = 0
        bpy.context.scene.render.simplify_child_particles_render = 0

        # Turn off everything else that might slow down rendering
        bpy.context.scene.eevee.use_volumetric_lights = False
        bpy.context.scene.eevee.use_volumetric_shadows = False

        # Optional: Set to the lowest possible settings for lighting and reflections
        for light in bpy.data.lights:
            light.cycles.cast_shadow = False

    # Make sure the scene is updated with the new settings
    bpy.context.view_layer.update()


class SimpleAnimator:
    def __init__(self):
        self.total_frames = 0
        self.frame_index = 0
        self.frame_limit = 0
        self.update_frame_fn = None
        self.output_dir = None

    def on_new_sequence(self, update_frame_fn, frame_limit, output_dir):
        self.frame_index = 0
        self.frame_limit = frame_limit
        self.update_frame_fn = update_frame_fn
        self.output_dir = output_dir

    def animate_frame(self):
        if self.frame_index >= self.frame_limit:
            print("Animation complete")
            return False

        self.update_frame_fn(self.frame_index)

        # Set keyframe for relevant objects
        for obj in bpy.data.objects:
            if obj.animation_data:
                obj.keyframe_insert(data_path="location", frame=self.frame_index)
                obj.keyframe_insert(data_path="rotation_euler", frame=self.frame_index)
                obj.keyframe_insert(data_path="scale", frame=self.frame_index)

                # Handle shape keys for mesh objects
                if obj.type == "MESH" and obj.data.shape_keys:
                    for key_block in obj.data.shape_keys.key_blocks:
                        obj.data.shape_keys.keyframe_insert(
                            data_path=f'key_blocks["{key_block.name}"].value',
                            frame=self.frame_index,
                        )

        # Render frame if output_dir is specified
        if self.output_dir:
            bpy.context.scene.frame_set(self.total_frames)
            bpy.context.scene.render.filepath = os.path.join(
                self.output_dir, f"frame_{self.total_frames:04d}.png"
            )
            bpy.ops.render.render(write_still=True)

        self.frame_index += 1
        self.total_frames += 1
        print(f"Animating frame {self.frame_index}")
        return True

    def is_running(self):
        return self.frame_index < self.frame_limit


class AnimationOperator(bpy.types.Operator):
    bl_idname = "wm.animation_operator"
    bl_label = "Animation Operator"

    _timer = None
    _animator = None
    _sequences = None
    _current_sequence = 0
    _total_frames = 0
    broadcast_root = None
    output_dir = None

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(FRAME_TIME_SEC, window=context.window)
        wm.modal_handler_add(self)
        self._animator = SimpleAnimator()
        self._sequences = _load_broadcast_index(self.broadcast_root)["sequences"]
        self.start_next_sequence()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if not self._animator.is_running():
                self._current_sequence += 1
                if self._current_sequence >= len(self._sequences):
                    self.finish_animation(context)
                    return {"FINISHED"}
                self.start_next_sequence()
            else:
                bpy.context.scene.frame_set(
                    self._total_frames + self._animator.frame_index
                )
                if not self._animator.animate_frame():
                    self.finish_animation(context)
                    return {"FINISHED"}

        return {"PASS_THROUGH"}

    def start_next_sequence(self):
        sequence = self._sequences[self._current_sequence]
        scene_func = SEQUENCE_TYPE_TO_FUNCTION[sequence["type"]]
        update_frame_fn = scene_func(self.broadcast_root, sequence["parameters"])
        frame_limit = int(sequence["duration_sec"] * RENDER_FPS)
        self._animator.on_new_sequence(update_frame_fn, frame_limit, self.output_dir)

    def finish_animation(self, context):
        self._total_frames += self._animator.frame_index
        bpy.context.scene.frame_end = self._total_frames
        if not self.output_dir:
            bpy.context.scene.render.filepath = "//rendered_animation_"
        print("Animation complete.")

        # Unregister the operator class
        if not DEBUG:
            bpy.utils.unregister_class(AnimationOperator)
            sys.exit(0)

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def start_scene(broadcast_root: str, output_dir: str = None):
    if output_dir and not DEBUG:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        AnimationOperator.output_dir = output_dir

    if not os.path.exists(broadcast_root):
        raise ValueError(f"Broadcast root does not exist: {broadcast_root!r}")

    AnimationOperator.broadcast_root = broadcast_root
    bpy.utils.register_class(AnimationOperator)
    setup_blender_scene()
    bpy.ops.wm.animation_operator("INVOKE_DEFAULT")
