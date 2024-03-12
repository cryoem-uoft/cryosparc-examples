#!/usr/bin/env python
# run pip install cryosparc-tools if you haven't already
from cryosparc.tools import CryoSPARC
import json
from pathlib import Path
import argparse
import re
from numpy import isclose

proj_string_pattern = r"(P[0-9]+),(W[0-9]+),(J[0-9]+)"

with open(Path.home() / 'instance-info.json', 'r') as f:
    instance_info = json.load(f)

cs = CryoSPARC(**instance_info)
assert cs.test_connection()

parser = argparse.ArgumentParser()
parser.add_argument(
    'project_string',
    help = "Project, Workspace, and Job separated by commas (no spaces). P100,W2,J26"
)
parser.add_argument(
    'apix',
    help = "New pixel size",
    type = float
)

args = parser.parse_args()

def main(args):
    match = re.match(proj_string_pattern, args.project_string)
    project_name = match.group(1)
    workspace_name = match.group(2)
    job_name = match.group(3)

    project = cs.find_project(project_name)

    extract_job = project.find_job(job_name)

    micrographs = extract_job.load_output("micrographs")

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
        name='micrographs',
        slots=["micrograph_blob", "rigid_motion", "background_blob", "movie_blob", "spline_motion", "micrograph_blob_non_dw"],
        passthrough=(job_name, 'micrographs'),
        title='micrographs_pix_updated'
    )
    new_job=project.find_job(updated_apix_job_name)
    new_micrographs=new_job.load_output("micrographs")

    for param in parameters_to_update:
        assert isclose(args.apix, new_micrographs[param])

    print(f'Updated pixel size in {updated_apix_job_name} is {args.apix}')

main(args)
