from late_now.plan_broadcast._types import (
    AudioFragments,
)
import json
import os
from dataclasses import dataclass
import tempfile
from scipy.io.wavfile import write as write_wav
import subprocess
import pkg_resources


@dataclass(frozen=True)
class BlendshapeCoefficients:
    # 52 coefficients, ARKit style
    values: list[float]


@dataclass(frozen=True)
class BlendshapeData:
    # 52 coefficients, ARKit style
    blendshape_frames: list[BlendshapeCoefficients]
    blendshape_name_to_index: dict[str, int]


ANIPORTRAIT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "models", "AniPortrait"
    )
)
BROADCAST_ROOT = pkg_resources.resource_filename(__name__, "assets/broadcasts/main/")


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


def _convert_json_to_blendshape_data(blendshapes_raw: dict) -> BlendshapeData:
    blendshape_names_to_indices: dict[str, int] = blendshapes_raw[
        "blendshape_names_to_indices"
    ]
    blendshape_coefs = blendshapes_raw["blendshape_coefs"]

    return BlendshapeData(
        blendshape_frames=[
            BlendshapeCoefficients(values=coefs) for coefs in blendshape_coefs
        ],
        blendshape_name_to_index=blendshape_names_to_indices,
    )


def _blendshapes_for_fragment(
    audio_fragment: AudioFragments, fps: int
) -> BlendshapeData:
    # TODO: Actually use FPS
    with tempfile.TemporaryDirectory() as tempdir:
        # create tmpfiule for wav data
        tmp_wav_file = os.path.join(tempdir, "audio.wav")
        tmp_json_file = os.path.join(tempdir, "output_blendshapes.json")

        # TODO: standardize on sample rate
        write_wav(tmp_wav_file, 24000, audio_fragment.audio)

        _execute_in_virtualenv(
            working_directory=ANIPORTRAIT_ROOT,
            virtualenv_path=os.path.join(ANIPORTRAIT_ROOT, ".venv"),
            commands=[
                "python -m scripts.audio_to_blendshapes -W 512 -H 512 "
                "--reference_image_path configs/inference/ref_images/walter.png"
                f" --audio_path {tmp_wav_file} --output-json {tmp_json_file}"
            ],
        )

        with open(tmp_json_file, "r") as f:
            blendshapes_raw = json.load(f)

        return _convert_json_to_blendshape_data(blendshapes_raw)


def _merge_blendshapes(
    blendshape_data_and_fragment: list[tuple[BlendshapeData, AudioFragments]],
    fps: int,
) -> BlendshapeData:
    assert len(blendshape_data_and_fragment) > 0, "we need at least one"

    # Assert all of the blendshape data mappings match on the dictionaries
    for data, _ in blendshape_data_and_fragment[1:]:
        assert (
            blendshape_data_and_fragment[0][0].blendshape_name_to_index
            == data.blendshape_name_to_index
        )

    blendshape_index_to_name = blendshape_data_and_fragment[0][
        0
    ].blendshape_name_to_index

    last_start_time = blendshape_data_and_fragment[-1][1].absolute_start_time_sec
    last_duration = blendshape_data_and_fragment[-1][1].duration_sec
    expected_total_length_frames = int((last_start_time + last_duration) * fps)

    merged_frames = []
    end_of_previous_segment_sec = 0

    for blendshape_data, fragment in blendshape_data_and_fragment:
        frames_to_extend = []

        start_of_current_fragment_sec = fragment.absolute_start_time_sec
        gap_length_sec = start_of_current_fragment_sec - end_of_previous_segment_sec

        end_of_current_fragment_sec = (
            start_of_current_fragment_sec + fragment.duration_sec
        )

        # Fill the gap between the end of the previous fragment and the start of the current fragment
        expected_fragment_frames = int(
            (end_of_current_fragment_sec - end_of_previous_segment_sec) * fps
        )

        gap_frames = int(gap_length_sec * fps)
        for _ in range(gap_frames):
            frames_to_extend.append(BlendshapeCoefficients(values=[0.0] * 52))

        assert len(frames_to_extend) == gap_frames, "Gap length mismatch"
        # Append the blendshape data for the current fragment
        frames_to_extend.extend(blendshape_data.blendshape_frames)

        # For some reason the model doesn't always predict a perfect number of frames
        # so we need to make sure the length of the blendshape data matches the expected length
        tail_end_fill_frames = expected_fragment_frames - len(frames_to_extend)
        if tail_end_fill_frames < 0:
            print(f"WARNING HAD TO TRUNCATE FRAMES: {tail_end_fill_frames}")
            frames_to_extend = frames_to_extend[:expected_fragment_frames]
        else:
            for _ in range(tail_end_fill_frames):
                frames_to_extend.append(BlendshapeCoefficients(values=[0.0] * 52))

        assert len(frames_to_extend) == expected_fragment_frames, "Length mismatch"

        merged_frames.extend(frames_to_extend)
        end_of_previous_segment_sec = end_of_current_fragment_sec

    if len(merged_frames) < expected_total_length_frames:
        tail_end_fill_frames = expected_total_length_frames - len(merged_frames)
        for _ in range(tail_end_fill_frames):
            merged_frames.append(BlendshapeCoefficients(values=[0.0] * 52))

    assert expected_total_length_frames == len(merged_frames), "Length mismatch"

    return BlendshapeData(
        blendshape_name_to_index=blendshape_index_to_name,
        blendshape_frames=merged_frames,
    )


def generate_blendshapes(
    speech_fragments: list[AudioFragments],
    *,
    fps: int,
) -> BlendshapeData:
    fragments_and_blendshapes = []
    for fragment in speech_fragments:
        fragments_and_blendshapes.append(
            (
                _blendshapes_for_fragment(fragment, fps=fps),
                fragment,
            )
        )

    return _merge_blendshapes(fragments_and_blendshapes, fps=fps)
