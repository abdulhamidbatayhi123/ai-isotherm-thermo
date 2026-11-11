# Launch records

These are the exact command files that started the long runs on the author's Windows machine (one file per shard or
job, started hidden so that a run outlives the terminal). They are kept unchanged as a record of how each result file
was produced, so they contain that machine's absolute paths. To rerun a job elsewhere, run the Python command inside
the file from the repository root with the interpreter of the environment in `requirements-lock.txt`, for example

    python scripts/run_confirmatory.py --shard 0/4

The run records in `results/` do not depend on these paths.
