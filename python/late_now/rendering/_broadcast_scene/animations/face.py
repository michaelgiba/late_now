# Allowed keys
def smooth_interpolation(t, x, lower_x, higher_x, lower_output, higher_output):
    # print(t, x, lower_x, higher_x, lower_output, higher_output)
    t = (x - lower_x) / (higher_x - lower_x)
    t = min(1, max(0, t))
    return lower_output + (higher_output - lower_output) * t


ALLOWED_KEYS = [
    "browDownLeft",
    "browDownRight",
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    "eyeBlinkLeft",
    "eyeBlinkRight",
    "eyeLookDownLeft",
    "eyeLookDownRight",
    "eyeLookInLeft",
    "eyeLookInRight",
    "eyeLookOutLeft",
    "eyeLookOutRight",
    "eyeLookUpLeft",
    "eyeLookUpRight",
    "eyeSquintLeft",
    "eyeSquintRight",
    "eyeWideLeft",
    "eyeWideRight",
    "jawForward",
    "jawLeft",
    "jawRight",
    "jawOpen",
    "mouthClose",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthFrownLeft",
    "mouthFrownRight",
    "mouthFunnel",
    "mouthLeft",
    "mouthRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthPucker",
    "mouthRollLower",
    "mouthRollUpper",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "noseSneerLeft",
]

RENAMES = {
    "tongueOut": "tongueOut",
    "Look Left": "eyeLookOutLeft",
    "Look Rigth": "eyeLookOutRight",
    "Look Up": "eyeLookUpLeft",
    "Look Down": "eyeLookDownLeft",
}

WEIGHTS = {
    "browDownLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "browDownRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "browInnerUp": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "browOuterUpLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "browOuterUpRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "cheekPuff": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "eyeLookDownLeft": 0.5,
    "eyeLookDownRight": 0.5,
    "eyeLookOutRight": 0.5,
    "eyeLookUpLeft": 0.5,
    "eyeLookUpRight": 0.5,
    "eyeSquintLeft": 0.5,
    "eyeSquintRight": 0.5,
    "eyeWideLeft": 0.5,
    "eyeWideRight": 0.5,
    # "jawForward": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    # "jawLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    # "jawRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "jawOpen": lambda x: smooth_interpolation("jawOpen", x, 0.96, 1, 0.5, 1.5),
    # "mouthClose": lambda x: smooth_interpolation("mouthClose", x, 0.45, 1, 0.0, 0.8),
    "mouthDimpleLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthDimpleRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthFrownLeft": lambda x: 0.9 + min(x**2, 0.1),
    "mouthFrownRight": lambda x: 0.9 + min(x**2, 0.1),
    "mouthFunnel": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthLowerDownLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthLowerDownRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthPressLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthPressRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthPucker": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthRollLower": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthRollUpper": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthSmileLeft": lambda x: 0.01,
    "mouthSmileRight": lambda x: 0.01,
    "mouthStretchLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthStretchRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthUpperUpLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "mouthUpperUpRight": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
    "noseSneerLeft": lambda x: smooth_interpolation("t", x, 0, 1.0, 0, 2.0),
}


def load_targets(input_mesh):
    shape_key_dict = {}

    def extract_shape_keys(obj):
        if obj.type == "MESH" and obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                if key.name != "Basis" and key.name not in shape_key_dict:
                    shape_key_dict[key.name] = obj

    # Check the input mesh itself
    extract_shape_keys(input_mesh)

    # Check all children
    for child in input_mesh.children:
        extract_shape_keys(child)

    return shape_key_dict


def weighted_value(key, xi):
    # get weight or reset to 1
    weight = WEIGHTS.get(key, 1)
    if callable(weight):
        return weight(xi)
    elif isinstance(weight, (int, float)):
        return weight * xi
    else:
        return xi


def _set_shape_key_value(obj, key_name, value):
    if obj.type == "MESH" and obj.data.shape_keys:
        key_block = obj.data.shape_keys.key_blocks.get(key_name)
        if key_block:
            key_block.value = value
            return True
    return False


def set_shape_key_values(shape_key_name_to_obj, shape_key_values):
    success = []

    for key_name, value in shape_key_values.items():
        wi = weighted_value(key_name, value)
        obj = shape_key_name_to_obj.get(key_name)
        if obj and _set_shape_key_value(obj, key_name, wi):
            success.append(key_name)

    return success
