#!/usr/bin/env python
from cryosparc.tools import CryoSPARC
import json
import re
from pathlib import Path
import argparse


def main(args):
    with open(Path(args.credentials).expanduser(), "r") as f:
        cs = CryoSPARC(**json.load(f))

    if not cs.test_connection():
        raise ConnectionError(
            "Connection to CryoSPARC failed. Check your instance info JSON file and network"
        )

    # this removeprefix shuffle ensures that the puid always starts with
    # a P, whether the user put one or not
    project = cs.find_project(puid := f"P{args.project.removeprefix('P')}")
    job = project.find_job(juid := f"J{args.job.removeprefix('J')}")

    if args.outdir is not None:
        outdir = Path(args.outdir).expanduser().resolve()
    else:
        outdir = Path(f"{puid}_{juid}_plots")

    if not outdir.exists():
        outdir.mkdir(parents=True)

    iter_pattern = None
    if args.iteration is not None:
        iter_pattern = re.compile(f"iteration_({int(args.iteration):0>3})")

    file_types = []
    if args.include_type is not None:
        file_types = args.include_type.replace(".", "").split(",")

    exclude_file_types = set()
    if args.exclude_type is not None:
        exclusions = set(args.exclude_type.replace(".", "").split(","))
        exclude_file_types = exclusions - set(file_types)

    plots_downloaded = 0
    for plot in job.list_assets():
        filename = plot["filename"]
        ftype = Path(filename).suffix.replace(".", "")
        if iter_pattern and re.search(iter_pattern, filename) is None:
            continue

        if file_types:
            if ftype not in file_types:
                continue
        if exclude_file_types:
            if ftype in exclude_file_types:
                continue

        # several plots just have the name "image.png", so they'd overwrite each other
        outname = Path(plot["filename"])
        base_name = outname.stem
        copy_index = 0
        while (outdir / outname).exists():
            outname = Path(str(base_name) + f"_{copy_index:0>2}" + str(outname.suffix))
            copy_index += 1

        job.download_asset(plot["_id"], outdir / outname)
        plots_downloaded += 1

    print(f"Downloaded {plots_downloaded} files")

    if not args.no_zip:
        import shutil

        shutil.make_archive(str(outdir), "zip", str(outdir))
        print(f"Zip file for download: {outdir.absolute()}.zip")


parser = argparse.ArgumentParser()
parser.add_argument("credentials", help="Credentials JSON file")
parser.add_argument("project", help="Project UID, like P123")
parser.add_argument("job", help="Job UID to download plots, like J123")
parser.add_argument(
    "--include-type",
    help="Comma-separated list of file extensions to save, like pdf,png. Default is all filetypes",
)
parser.add_argument(
    "--exclude-type",
    help="Comma-separated list of filetypes to exclude. Default `txt`. Inclusions override exclusions.",
    default="txt",
)
parser.add_argument(
    "--iteration",
    help="Download only the specified iteration. If you don't specify one, all iterations will be downloaded.",
)
parser.add_argument(
    "--outdir",
    help="Directory into which plots are saved. Default <project>_<job>_plots",
)
parser.add_argument(
    "--no-zip",
    help="Do not create a .zip archive of the downloaded plots",
    action="store_true",
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
