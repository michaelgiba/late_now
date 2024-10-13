import json
import argparse
import tempfile
from contextlib import contextmanager

from late_now.plan_broadcast._types import (
    ShowSegment,
    ResourceStagingArea,
)
from late_now.plan_broadcast.packaging import package_segment
from late_now.plan_broadcast.broadcast_definition import (
    create_broadcast_definition_bundle,
)


@contextmanager
def _resource_staging_area():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield ResourceStagingArea(tmpdir=tmpdir)


def packaging(args):
    # Read show structure from input file
    with open(args.input_structure_path, "r") as f:
        show_structure_data = json.load(f)

    # Convert back to ShowSegment objects
    show_structure = [ShowSegment.from_dict(segment) for segment in show_structure_data]
    with _resource_staging_area() as staging_area:
        packaged_segments = [
            package_segment(segment, staging_area) for segment in show_structure
        ]
        create_broadcast_definition_bundle(
            packaged_segments, staging_area, args.output_tar_path
        )


def _parse_args():
    parser = argparse.ArgumentParser(description="Package broadcast")
    parser.add_argument(
        "--input-structure-path",
        type=str,
        required=True,
        help="Path to input the show structure",
    )
    parser.add_argument(
        "--output-tar-path",
        type=str,
        required=True,
        help="Path to the output tar file",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    packaging(args)


if __name__ == "__main__":
    main()
