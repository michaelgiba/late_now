import pkg_resources

RENDER_FPS = 30
FRAME_TIME_MS = 1000.0 / RENDER_FPS
FRAME_TIME_SEC = 1.0 / RENDER_FPS
DEBUG = False


def get_resource_filename(filename):
    return pkg_resources.resource_filename(__name__, filename)


STATIC_MESHES = {
    "audience": get_resource_filename("assets/meshes/audience.glb"),
    "couch": get_resource_filename("assets/meshes/couch.glb"),
    "walter": get_resource_filename(
        "assets/meshes/fiverr_walter20240902_attempt_to_reduce_poly.blend1"
    ),
    "sax": get_resource_filename("assets/meshes/band/Saxophone.glb"),
    "drum": get_resource_filename("assets/meshes/band/DrumKit.glb"),
    "piano": get_resource_filename("assets/meshes/band/Piano.glb"),
    "bandMember": get_resource_filename("assets/meshes/band/Pablo.glb"),
}

STATIC_TEXTURES = {
    "background": get_resource_filename("assets/textures/bg2.png"),
    "logo_overlay": get_resource_filename("assets/textures/intro_overlay.png"),
}


STATIC_ANIMATIONS = {
    "intro": get_resource_filename("assets/animations/cool_intro.bvh"),
    "talking": get_resource_filename("assets/animations/talking.bvh"),
    "slapping": get_resource_filename("assets/animations/slapping.bvh"),
}
