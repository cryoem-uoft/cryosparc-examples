#!/usr/bin/env python
# run pip install cryosparc-tools if you haven't already
from cryosparc.tools import CryoSPARC
import json
from pathlib import Path
import argparse
import numpy as np

def ensure_prefix(s: str, prefix: str) -> str:
    return f"{prefix}{s.removeprefix(prefix)}"
def main(args):
    with open(Path(args.credentials).expanduser(), "r") as f:
        credentials = json.load(f)
    cs = CryoSPARC(**credentials)
    project_name = ensure_prefix(args.puid, "P")
    project = cs.find_project(project_name)

    job_name = ensure_prefix(args.juid, "J")
    micrograph_job = project.find_job(job_name)
    workspace_name = micrograph_job.doc["workspace_uids"][0]

    micrographs = micrograph_job.load_output(args.output)

    parameters_to_update=[
        "micrograph_blob/psize_A",
        "rigid_motion/psize_A",
        "background_blob/psize_A",
        "movie_blob/psize_A",
        "spline_motion/psize_A",
        "micrograph_blob_non_dw/psize_A"
    ]

    for param in parameters_to_update:
        micrographs[param] = args.apix

    updated_apix_job_name = project.save_external_result(
        workspace_uid=workspace_name,
        dataset=micrographs,
        type='exposure',
        name=args.output,
        slots=list(set(x.split("/")[0] for x in parameters_to_update)),
        passthrough=(job_name, args.output),
        title=f'{args.output}_pix_updated'
    )

    print(f'Updated pixel size in {updated_apix_job_name} is {args.apix}')

parser = argparse.ArgumentParser()
parser.add_argument(
    "puid",
    help = "Project UID from which to load micrographs. Like P123"
)
parser.add_argument(
    "juid",
    help = "Job UID from which to load micrographs. Like J456"
)
parser.add_argument(
    'apix',
    help = "New pixel size",
    type = float
)
parser.add_argument(
    "--output",
    help="Micrograph output name. Default: micrographs",
    default="micrographs"
)
parser.add_argument(
    "--credentials",
    help = "Location of a instance-info.json file. Default ~/instance-info.json",
    default="~/instance-info.json"
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
