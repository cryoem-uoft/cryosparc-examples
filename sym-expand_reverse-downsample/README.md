# Reverse downsampling of symmetry-expanded particles

This script takes symmetry-expanded particles which have been downsampled and replaces their `blob` fields with the appropriate values from the original, full-size images.

## Usage

```
./reverse-downsample.py http://localhost:39000 P392 J483 J480
```

where

 - Your CryoSPARC server is at http://localhost:39000
 - P392 is your project UID
 - J483 is the job you want to keep particle metadata from
 - J480 is the downsample particles job
