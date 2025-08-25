# Extracting Data About CryoSPARC Projects
Some use cases require programmatic access of information about a CryoSPARC instance or job.
For example, an Electronic Lab Notebook may require knowing the project and job UIDs associated with a particular map, and the final GSFSC resolution, mask, and particle stack used to create it.
Other cases may use an external database to associate e.g., the process used to purify protein with the final map quality for that prep.

This type of use, while important, is very context-specific, so no one-size-fits-all approach will exist.
However, the notebooks in this directory provide some guidance on how information like this may be extracted.
Functions and steps used in these notebooks could be combined into a script which is run on jobs of interest from the command line.