from dataclasses import dataclass
import os
import tempfile
import subprocess
import contextlib
from typing import Generator
import json


@dataclass
class Track:
    absolute_path: str
    track_type: str
    duration_sec: float


@dataclass
class RecordBroadcastOptions:
    output_uri: str
    input_tar_path: str


@dataclass
class RecordBroadcastContext:
    tmpdir_root: str
    options: RecordBroadcastOptions

    def __post_init__(self):
        os.makedirs(self.scratch_directory(), exist_ok=True)
        os.makedirs(self.broadcast_directory(), exist_ok=True)
        os.makedirs(self.track_storage_path(), exist_ok=True)

        print(
            f"Extracting {self.options.input_tar_path} to {self.broadcast_directory()}"
        )

        subprocess.run(
            [
                "tar",
                "-xzf",
                self.options.input_tar_path,
                "-C",
                self.broadcast_directory(),
                ".",
            ]
        )

    def scratch_directory(self) -> str:
        return os.path.join(self.tmpdir_root, "scratch")

    def broadcast_directory(self) -> str:
        return os.path.join(self.tmpdir_root, "broadcast")

    def track_storage_path(self) -> str:
        return os.path.join(self.tmpdir_root, "tracks")

    def broadcast_definition(self) -> dict:
        with open(os.path.join(self.broadcast_directory(), "index.json")) as f:
            return json.load(f)


@contextlib.contextmanager
def new_broadcast_context(
    options: RecordBroadcastOptions,
) -> Generator[RecordBroadcastContext, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            yield RecordBroadcastContext(tmpdir_root=tmpdir, options=options)
        finally:
            pass
