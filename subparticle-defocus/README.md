# Adjust subparticle defocus

> [!NOTE]
> This script is the result of extended conversation in [this forum thread](https://discuss.cryosparc.com/t/adjust-per-particle-defocus-of-subparticles-in-volume-alignment-tools/14718).
> Please visit that link for more information on the problem being solved here.

This script adjusts the defocus of individual "subparticles".

Consider a large symmetric object like a virus.
Processing these objects in smaller "subparticles" (typically focused on a single asymmetric unit)
provides many benefits, not least of which is a tractable box size.
A typical workflow for extracting these subparticles might look as follows:

1. The entire particle is refined
2. The particles are symmetry expanded
3. The volume is shifted to center one of the subparticles. Because of symmetry expansion, each particle is essentially shifted N times to each of the N asymmetric units.
4. A smaller image of each ASU is extracted and used downstream.

This script uses the shfit from step 3 to adjust each subparticle's defocus after extraction in step 4.
This is related to (but not interchangeable with) Ewald sphere correction.

# Usage

```
usage: adjust_defocus.py [-h] [--lane LANE] project workspace vat_job image_job

positional arguments:
  project      Project UID
  workspace    Workspace UID
  vat_job      VAT job used to recenter expanded particles
  image_job    Job with cropped images. Usually a Downsample Particles or Extract job

options:
  -h, --help   show this help message and exit
  --lane LANE  Lane on which to queue the reconstruct job. If unset, job is note queued.
```

For example, if in P1 W1 a Volume Alignment Tools job J123 was used to shift particles and an extract job J456 was used to extract the subparticles, and reconstructions should run on lane `worker1`:

```
adjust_defocus.py P1 W1 J123 J456 --lane worker1
```
