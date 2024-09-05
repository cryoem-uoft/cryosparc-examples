#!/usr/bin/env python
from cryosparc.tools import CryoSPARC
import json
import numpy as np
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

def main(args):
    with open(Path('~/instance-info.json').expanduser(), 'r') as f:
        instance_info = json.load(f)

    cs = CryoSPARC(**instance_info)
    assert cs.test_connection()

    project_uid = args.project
    workspace_uid = args.workspace
    job_uids = args.job

    project = cs.find_project(project_uid)

    flip_job = project.create_external_job(
        workspace_uid,
        "Flipped particles"
    )
    
    for jid in job_uids:
        job = project.find_job(jid)
        particles = job.load_output("particles")

        mic_uid = particles["location/micrograph_uid"][0]
        first_mic_particles = particles.query({"location/micrograph_uid": mic_uid})
        _, mic = project.download_mrc(first_mic_particles["location/micrograph_path"][0])
        mic = mic[0,:,:]
        height, width = mic.shape

        fig, ax = plt.subplots(figsize = (10,10))
        ax.axis(False)
        ax.imshow(
            mic,
            cmap = "Greys_r",
            origin = "lower",
            vmin = np.percentile(mic, 5),
            vmax = np.percentile(mic, 95)
        )

        ax.plot(
            first_mic_particles["location/center_x_frac"] * width,
            first_mic_particles["location/center_y_frac"] * height,
            color = "#2c2c2c",
            label= "Before flip",
            linestyle = "",
            marker = "o",
            markersize = 10,
            markeredgecolor = "white"
        )

        particles["location/center_y_frac"] = 1 - particles["location/center_y_frac"]

        ax.plot(
            first_mic_particles["location/center_x_frac"] * width,
            (1 - first_mic_particles["location/center_y_frac"]) * height,
            color = "#FAB06E",
            label = "After flip",
            linestyle = "",
            marker = "P",
            markersize = 10,
            markeredgecolor = "white"
        )
        ax.legend(loc = "lower left")

        particle_in_name = f"particles_{jid}"
        flip_job.add_input(
            type = "particle",
            name = particle_in_name
        )
        flip_job.connect(
            target_input = particle_in_name,
            source_job_uid = jid,
            source_output = "particles"
        )

        flip_job.add_output(
            type = "particle",
            name = particle_in_name,
            title = f"Flipped particles from {jid}",
            slots = ["location"],
            passthrough = particle_in_name,
            alloc = particles
        )
        flip_job.save_output(particle_in_name, particles)

        flip_job.log_plot(fig, f"Before/after flip for {jid}")
    
    flip_job.stop()



parser = argparse.ArgumentParser(
    usage="Flip particle coordinates in Y"
)
parser.add_argument(
    "project",
    help = "Project UID, e.g., P123"
)
parser.add_argument(
    "workspace",
    help = "Workspace UID, e.g., W3"
)
parser.add_argument(
    "job",
    help = "Job(s) with particles to flip. Give as space-separated list, e.g., J1 J2 J3 J4",
    nargs="+",
    metavar="job(s)"
)

if __name__ == "__main__":
    args = parser.parse_args()
    args.project = args.project if "P" in args.project else f"P{args.project}"
    args.workspace = args.workspace if "W" in args.workspace else f"W{args.workspace}"
    args.job = [jid if "J" in jid else f"J{jid}" for jid in args.job]

    main(args)