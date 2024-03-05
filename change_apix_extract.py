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

def main(args):
    match = re.match(proj_string_pattern, args.project_string)
    project_name = match.group(1)
    workspace_name = match.group(2)
    job_name = match.group(3)

    project = cs.find_project(project_name)

    particles_job = project.find_job(job_name)

    particles = particles_job.load_output("particles")

    new_apix = args.apix
    print(f"Changing pixel size from {particles['blob/psize_A'][0]} to {new_apix}")
    particles["blob/psize_A"] = new_apix

    updated_apix_job_name = project.save_external_result(
        workspace_uid=workspace_name,
        dataset=particles,
        type='particle',
        name='particles',
        slots=['blob'],
        passthrough=(job_name, 'particles'),
        title='change_angpix_particles'
    )
    new_job=project.find_job(updated_apix_job_name)
    new_particles=new_job.load_output("particles")
    assert isclose(new_apix, new_particles['blob/psize_A'][0]), 'Pixel size did not change. This should not happen.'
    print(f'Updated pixel size in {updated_apix_job_name}')

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
main(args)