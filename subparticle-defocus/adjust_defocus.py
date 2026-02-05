#!/usr/bin/env python
import cryosparc
import numpy as np
from cryosparc.tools import CryoSPARC
import json
from pathlib import Path
import argparse
import re
from scipy.spatial.transform import Rotation as R

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cryosparc.controllers.job
    from numpy.typing import NDArray

with open(Path("~/instance-info.json").expanduser(), "r") as f:
    instance_info = json.load(f)

cs = CryoSPARC(**instance_info)
assert cs.test_connection()


def ensure_prefix(prefix: str, suffix: str) -> str:
    return f"{prefix if not suffix.startswith(prefix) else ''}{suffix}"


recenter_pattern = re.compile(r"([\.\d]+), ?([\.\d]+), ?([\.\d]+) ?(px|A)?")
mask_center_pattern = re.compile(
    r"^New center will be located at voxel coordinates: ([\.\d]+), ([\.\d]+), ([\.\d]+) \(x,y,z\)$"
)


def get_param_center(
    job: "cryosparc.controllers.job.JobController", apix: float
) -> "NDArray[np.floating]":
    recenter_match = re.match(recenter_pattern, job.params.recenter_shift)
    if recenter_match is None:
        raise ValueError("Center parameter was set but could not be parsed")
    x, y, z, units = recenter_match.groups()
    if units is None:
        units = "px"
    center = np.array(list(float(d) for d in (x, y, z)))
    if units.lower() == "px":
        center = center * apix

    return center


def get_mask_center(
    job: "cryosparc.controllers.job.JobController",
    apix: float,
    cs: CryoSPARC,
    puid: str,
):
    for event in cs.api.jobs.get_event_logs(puid, job.uid):
        try:
            match = re.match(mask_center_pattern, event.text)
        except AttributeError:
            continue
        if match is not None:
            x, y, z = match.groups()
            x, y, z = (float(d) for d in (x, y, z))
            return np.array([x, y, z]) * apix


def main(args):
    puid = ensure_prefix("P", args.project)
    wuid = ensure_prefix("W", args.workspace)
    vat_juid = ensure_prefix("J", args.vat_job)
    particles_juid = ensure_prefix("J", args.image_job)

    project = cs.find_project(puid)
    vat_job = project.find_job(vat_juid)
    volume = vat_job.load_output("volume")
    particles_job = project.find_job(particles_juid)
    particles = particles_job.load_output("particles")

    apix = volume["map/psize_A"][0]
    map_size_px = volume["map/shape"][0][0]
    map_size_a = map_size_px * apix
    # recenter_vector_a points from the old center to the new center in the reference frame
    try:
        recenter_vector_a = get_param_center(vat_job, apix)
    except TypeError:
        recenter_vector_a = get_mask_center(vat_job, apix, cs, puid)
    recenter_vector_a -= map_size_a / 2

    # cs poses rotate particles' frames into volume's frame, we want to rotate
    # the volume's frame into particles'
    rotations = R.from_rotvec(particles["alignments3D/pose"]).inv()

    # shifts is recenter_vector_a in the particle's frame
    shifts = rotations.apply(recenter_vector_a)

    # when recenter vector has a positive Z we moved the volume toward the
    # beam source, so we want to *subtract* from the defocus
    for column in ["ctf/df1_A", "ctf/df2_A"]:
        particles[column] -= shifts[:, 2]

    out_job = project.create_external_job(
        workspace_uid=wuid, title="Defocus-adjusted particles SUBTRACT"
    )
    out_job.add_input(
        type="particle", name="input_particles", slots=["alignments3D", "ctf"]
    )
    out_job.connect(
        target_input="input_particles",
        source_job_uid=particles_juid,
        source_output="particles",
    )
    out_job.add_output(
        type="particle",
        name="particles",
        passthrough="input_particles",
        slots=["ctf"],
        alloc=particles,
    )
    with out_job.run(), open(__file__, "r") as f:
        out_job.save_output("particles", particles)
        out_job.log("# Job Script ---------")
        out_job.log("".join(f))
        out_job.log("# Arguments ----------")
        out_job.log(str(vars(args)))

    if args.lane:
        recon_job = project.create_job(
            wuid,
            type="homo_reconstruct",
            title="Reconstruction SUBTRACT",
            connections={"particles": (out_job.uid, "particles")},
        )
        recon_job.queue(args.lane)

    for column in ["ctf/df1_A", "ctf/df2_A"]:
        particles[column] += 2 * shifts[:, 2]

    out_job = project.create_external_job(
        workspace_uid=wuid, title="Defocus-adjusted particles ADD"
    )
    out_job.add_input(
        type="particle", name="input_particles", slots=["alignments3D", "ctf"]
    )
    out_job.connect(
        target_input="input_particles",
        source_job_uid=particles_juid,
        source_output="particles",
    )
    out_job.add_output(
        type="particle",
        name="particles",
        passthrough="input_particles",
        slots=["ctf"],
        alloc=particles,
    )
    with out_job.run(), open(__file__, "r") as f:
        out_job.save_output("particles", particles)
        out_job.log("# Job Script ---------")
        out_job.log("".join(f))
        out_job.log("# Arguments ----------")
        out_job.log(str(vars(args)))

    if args.lane:
        recon_job = project.create_job(
            wuid,
            type="homo_reconstruct",
            title="Reconstruction ADD",
            connections={"particles": (out_job.uid, "particles")},
        )
        recon_job.queue(args.lane)


parser = argparse.ArgumentParser()
parser.add_argument("project", help="Project UID")
parser.add_argument("workspace", help="Workspace UID")
parser.add_argument("vat_job", help="VAT job used to recenter expanded particles")
parser.add_argument(
    "image_job",
    help="Job with cropped images. Usually a Downsample Particles or Extract job",
)
parser.add_argument(
    "--lane",
    help="Lane on which to queue the reconstruct job. If unset, job is note queued.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
