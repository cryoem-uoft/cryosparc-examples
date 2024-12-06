#!/usr/bin/env python

from cryosparc.tools import CryoSPARC
import json
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
import argparse

def make_histogram(x_component, bins, ax = None):    
    if ax is None:
        ax = plt.gca()

    hist, _, _ = ax.hist(
        x_component,
        density = False,
        bins = bins
    )

    ax.set_xlim(-1.5, 1.5)
    ax.set_aspect(3 / max(hist))

def make_2d_hist(x_component, y_component, ax = None, norm = "linear", **kwargs):
    # use our own norm argument instead of **kwargs b/c handling of string args to norm in ax.hexbin
    # is broken in the version of MPL shipped with CS
    if norm == "log":
        normalizer = LogNorm()
    else:
        normalizer = None
    if norm not in ["log", "linear", None]:
        print(f"Warning: normalizer '{norm}' not implemented. Using linear scale.")
    
    if "norm" in kwargs:
        del kwargs["norm"]

    if ax is None:
        ax = plt.gca()

    heatmap = ax.hist2d(
        x_component,
        y_component,
        cmin = 10,
        range = [
            [-1.5, 1.5],
            [-1.5, 1.5]
        ],
        norm = normalizer,
        **kwargs
    )

    ax.set_xlim(-1.5, 1.5)
    ax.set_aspect(1)

    return heatmap

def main(args):
    with open(Path('~/instance-info.json').expanduser(), 'r') as f:
        instance_info = json.load(f)

    cs = CryoSPARC(**instance_info)
    assert cs.test_connection()

    project_uid = args.puid if "P" in args.puid else f"P{args.puid}"
    project = cs.find_project(project_uid)

    job_uid = args.juid if "J" in args.juid else f"J{args.juid}"
    job = project.find_job(job_uid)

    particles = job.load_output("particles")
    latent_fields = [x for x in particles.fields() if "component" in x and "value" in x]
    # 2 dimensions is the default
    num_latents = job.doc["params_spec"].get("flex_K", {"value": 2})["value"]

    latent_coords = np.array(particles.filter_fields(latent_fields, copy = True).to_list(exclude_uid = True))
    # plots in the training job are jittered, so we should do the same for consistency unless the user
    # tells us not to
    if not args.no_jitter:
        jitter = np.random.default_rng().normal(scale = 0.05, size = latent_coords.shape)
        latent_coords += jitter

    fig_size = np.min([5 * num_latents, 16])

    fig, axs = plt.subplots(
        nrows = num_latents,
        ncols = num_latents,
        sharex = True,
        sharey = False,
        layout = "compressed",
        figsize = (fig_size, fig_size)
    )

    for column in range(num_latents):
        for row in range(num_latents):
            if column == row:
                make_histogram(
                    latent_coords[:, column],
                    bins = args.bins,
                    ax = axs[column, row]
                )
            elif column > row and not args.no_log_plots:
                heatmap = make_2d_hist(
                    latent_coords[:, row],
                    latent_coords[:, column],
                    axs[column, row],
                    norm = "log",
                    bins = args.bins
                )
                fig.colorbar(
                    heatmap[3],
                    ax = axs[column, row],
                    location = "bottom",
                    pad = 0.025,
                    fraction = 0.05
                )
            elif column < row and not args.no_linear_plots:
                heatmap = make_2d_hist(
                    latent_coords[:, row],
                    latent_coords[:, column],
                    axs[column, row],
                    norm = "linear",
                    bins = args.bins
                )
                fig.colorbar(
                    heatmap[3],
                    ax = axs[column, row],
                    location = "bottom",
                    pad = 0.025,
                    fraction = 0.05
                )
            else:
                axs[column, row].set_axis_off()


            if column == 0:
                axs[column, row].set_title(f"Component {row}")
            if row == 0:
                axs[column, row].set_ylabel(f"Component {column}")

    job.log_plot(fig, "All coordinates")
    job.log(f"Plots added with {__file__}")

parser = argparse.ArgumentParser()
parser.add_argument(
    "puid",
    help = "Project UID"
)
parser.add_argument(
    "juid",
    help = "Job UID of 3D Flex Train job"
)
parser.add_argument(
    "--bins",
    help = "Number of bins in histograms. Default 45",
    type = int,
    default = 45
)
parser.add_argument(
    "--no-log-plots",
    help = "Do not plot log-scaled heatmaps on the lower half of the plot",
    action = "store_true"
)
parser.add_argument(
    "--no-linear-plots",
    help = "Do not plot linear-scaled heatmaps on the upper half of the plot",
    action = "store_true"
)
parser.add_argument(
    "--no-jitter",
    help = "During trainig, latent plots are 'jittered' to smooth out their appearance. This parameter turns off jittering for these plots.",
    action = "store_true"
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)