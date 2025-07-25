# Changing Pixel Size

The scripts in this directory create a new output with an updated pixel size, perhaps found as a result of pixel size calibrations performed using earlier results.

## `change_apix_extract.py`

This script changes the pixel size of all particles in a stack to a provided value.
Note that only particle metadata is changed, and it is only changed for the new particle output this job creates.
No existing jobs are modified.
Note also that the micrograph pixel sizes are *not* changed, so if the particles are re-extracted their pixel sizes will revert to the old value.

Example usage:
```
change_apix_extract.py P123,W2,J456 1.008
```

## `change_apix_micrographs.py`

This script changes all of the pixel size fields of a set of micrographs.

Example usage:
```
change_apix_micrographs.py P123,W2,J456 1.008
```