from abc import ABC
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import os
import subprocess
import numpy as np


class SequenceType(Enum):
    INTRO = "intro"
    BROADCAST = "broadcast"
    OUTRO = "outro"


class BroadcastCameraCutType(Enum):
    BAND = "band"
    FLY_IN = "fly_in"
    MAIN = "main"
    PERSONA = "persona"
    SIDE_LEFT = "side_left"
    SIDE_RIGHT = "side_right"


class SequenceParameters(ABC):
    pass


@dataclass
class IntroParameters(SequenceParameters):
    text: str
    image: str  # The path to the image that shows on the background TV
    audio: str  # The path to the blended audio that plans during the broadcast (voiceover, music, etc)


@dataclass
class BroadcastCameraCut:
    camera: str
    duration_sec: float


@dataclass
class BroadcastParameters(SequenceParameters):
    text: str
    image: str  # The path to the image that shows on the background TV
    audio: str  # The path to the blended audio that plans during the broadcast (voiceover, music, etc)
    character_to_animation: dict[str, str]  # The path to the animation data
    camera_cuts: list[BroadcastCameraCut]
    full_text_transcript: str


@dataclass
class SequenceDefinition:
    type: SequenceType
    parameters: BroadcastParameters
    duration_sec: float

    def to_json(self):
        return {
            "type": self.type.value,
            "parameters": asdict(self.parameters),
            "duration_sec": self.duration_sec,
        }


@dataclass
class BroadcastDefintion:
    title: str
    sequences: list[SequenceDefinition]

    def to_json(self):
        return {
            "title": self.title,
            "sequences": [sequence.to_json() for sequence in self.sequences],
        }


@dataclass
class SegmentScriptLine:
    line_type: str  # 'walter' or 'sound'
    content: dict

    def to_dict(self):
        return {
            "line_type": self.line_type,
            "content": self.content,
        }


@dataclass
class SegmentDetailedScript:
    """
    (sound: intro_music)
    WALTER: Knock knock
    (sound: laughter)
    WALTER: How can I help you today?
    (sound: applause)
    WALTER: me?
    (sound: applause)
    """

    lines: list[SegmentScriptLine]

    def to_dict(self):
        return {"lines": [line.to_dict() for line in self.lines]}


@dataclass
class ShowSegment:
    sequence_type: SequenceType
    source_material: dict
    detailed_script: SegmentDetailedScript

    def plain_text(self) -> str:
        return "\n".join(
            line.content["text"]
            for line in self.detailed_script.lines
            if line.line_type == "dialog"
        )

    def to_dict(self):
        return {
            "sequence_type": self.sequence_type.name,
            "source_material": self.source_material,
            "detailed_script": self.detailed_script.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            sequence_type=SequenceType[data["sequence_type"]],
            source_material=data["source_material"],
            detailed_script=SegmentDetailedScript(
                lines=[
                    SegmentScriptLine(
                        line_type=line["line_type"],
                        content=line["content"],
                    )
                    for line in data["detailed_script"]["lines"]
                ]
            ),
        )


@dataclass(frozen=True)
class AudioFragments:
    absolute_start_time_sec: float
    audio_type: str
    audio: np.ndarray
    duration_sec: float
    sentence: str
    line_body_motion: str | None


@dataclass(frozen=True)
class AudioGeneration:
    total_duration_sec: float
    relative_audio_path: str
    audio_fragments: list[AudioFragments]


@dataclass(frozen=True)
class PackagedShowSegment:
    segment: ShowSegment

    title: str
    audio_generation: AudioGeneration
    relative_image_path: str
    character_name_to_relative_animation_path: dict[str, str]


@dataclass(frozen=True)
class ResourceStagingArea:
    tmpdir: str

    def __post_init__(self):
        os.makedirs(os.path.join(self.tmpdir, "audio"))
        os.makedirs(os.path.join(self.tmpdir, "image"))
        os.makedirs(os.path.join(self.tmpdir, "animation"))

    def to_relative(self, absolute_path: str) -> str:
        if not absolute_path.startswith(self.tmpdir):
            raise ValueError(f"Path {absolute_path} is not in the staging area")

        return os.path.relpath(absolute_path, self.tmpdir)

    def _get_unique_file_name(self, ext) -> str:
        # Short file name to be used for outputs
        return f"{str(uuid.uuid4())[:8]}.{ext}"

    def audio_path(self, *, ext: str) -> str:
        return os.path.join(self.tmpdir, "audio", self._get_unique_file_name(ext))

    def image_path(self, *, ext: str) -> str:
        return os.path.join(self.tmpdir, "image", self._get_unique_file_name(ext))

    def animation_path(self, *, ext: str) -> str:
        return os.path.join(self.tmpdir, "animation", self._get_unique_file_name(ext))

    def broadcast_definition_path(self) -> str:
        return os.path.join(self.tmpdir, "index.json")

    def bundle(self, output_tar_path: str):
        print(output_tar_path, self.tmpdir)
        subprocess.run(["tar", "-czf", output_tar_path, "-C", self.tmpdir, "."])
