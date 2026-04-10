#!/usr/bin/env python
import argparse
from cryosparc.tools import CryoSPARC
try:
    import polars as pl
except ImportError:
    import sys
    print("This script requires `polars`. Install with `pip install polars`.")
    sys.exit(1)

def ensure_prefix(p: str, s: str) -> str:
    return f"{p}{s.removeprefix(p)}"

def main(args):
    cs = CryoSPARC(args.hostname)
    project = cs.find_project(ensure_prefix("P", args.pid))
    source_job = project.find_job(ensure_prefix("J", args.source_jid))
    source_particles = source_job.load_output(args.source_particle_title)
    blob_fields = list(f for f in source_particles.fields() if f.startswith("blob"))
    ds_job = project.find_job(ensure_prefix("J", args.downsample_jid))
    full_size_particles = ds_job.load_input("particles").filter_prefix("blob")

    source_df = pl.DataFrame(source_particles.cols())
    source_df = source_df.drop(blob_fields)
    full_size_df = pl.DataFrame(full_size_particles.cols())
    merged_df = source_df.join(
        full_size_df,
        how="left",
        validate="m:1",
        left_on="sym_expand/src_uid",
        right_on="uid",
    )
    merged_df = merged_df.drop([c for c in merged_df.columns if c.endswith("_right")])

    for f in blob_fields:
        source_particles[f] = merged_df[f]
    
    

    dest_wuid = args.workspace_uid if args.workspace_uid else source_job.model.workspace_uids[0]
    out_job = project.create_external_job(
        workspace_uid = dest_wuid,
        title="Un-downsampled particles",
    )

    out_job.add_input(
        type="particle",
        name="particles",
        slots=["blob"],
    )
    out_job.connect(
        target_input="particles",
        source_job_uid=args.source_jid,
        source_output=args.source_particle_title,
    )
    out_job.add_output(
        "particle",
        "particles",
        slots=["blob"],
        passthrough="particles"
    )
    with out_job.run():
        out_job.save_output(
            name="particles",
            dataset=source_particles,
        )

        with open(__file__, "r") as f:
            out_job.log("===== script\n" + "".join(f))

        out_job.log("===== args\n" + str(vars(args)))


parser = argparse.ArgumentParser()
parser.add_argument(
    "hostname",
    help="CryoSPARC hostname, like http://localhost:39000",
)
parser.add_argument(
    "pid",
    help="Project UID, like P123",
)
parser.add_argument(
    "source_jid",
    help="Job uid for which particle blob will be replaced, like J123",
)
parser.add_argument(
    "downsample_jid",
    help="Job UID for downsample job, like J456",
)
parser.add_argument(
    "--source-particle-title",
    help="Title of the source job's particles output. Default 'particles'",
    default="particles",
)
parser.add_argument(
    "--workspace-uid",
    help="Workspace UID in which to export full-size particles. By default the first workspace of the source job.",
    default=None
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
