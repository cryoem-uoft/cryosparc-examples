# Extracting Data About CryoSPARC Projects
Some use cases require programmatic access of information about a CryoSPARC instance or job.
For example, an Electronic Lab Notebook may require knowing the project and job UIDs associated with a particular map, and the final GSFSC resolution, mask, and particle stack used to create it.
Other cases may use an external database to associate e.g., the process used to purify protein with the final map quality for that prep.

This type of use, while important, is very context-specific, so no one-size-fits-all approach will exist.
However, the notebooks in this directory provide some guidance on how information like this may be extracted.
Functions and steps used in these notebooks could be combined into a script which is run on jobs of interest from the command line.

# Downloading all plots from a job
CryoSPARC results are often presented externally by showing plots from a job. `download_all_plots.py` lets you download all plots from a job for convenience.

## Usage

```
positional arguments:
  credentials           Credentials JSON file, like ~/instance-info.json
  project               Project UID, like P123
  job                   Job UID to download plots, like J123

options:
  -h, --help            show this help message and exit
  --include-type INCLUDE_TYPE
                        Comma-separated list of file extensions to save, like pdf,png. Default is all filetypes
  --exclude-type EXCLUDE_TYPE
                        Comma-separated list of filetypes to exclude. Default `txt`. Inclusions override exclusions.
  --iteration ITERATION
                        Download only the specified iteration. If you don't specify one, all iterations will be downloaded.
  --outdir OUTDIR       Directory into which plots are saved. Default <project>_<job>_plots
  --no-zip              Do not create a .zip archive of the downloaded plots
```

## Examples

To download all plots from P123, J456:
```
python download_all_plots.py ~/instance-info.json P123 J456
```

To download only PDFs from iteration 3 of P123, J456
```
python download_all_plots.py ~/instance-info.json P123 J456 --include-type pdf --iteration 3
```
