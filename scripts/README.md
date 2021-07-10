# Scripts

This directory contains scripts that automatically collect, generate, or validate materials in the repository.

* `regularize_directories.py` ensures that packages directories are non-nested, that there is one Excel file per package directory, and that every package directory has a `views` subdirectory for storing generated artifacts.
* `export_csvs.py` exports a CSV from each user tab of a package Excel file into the corresponding `views` directory, in order to simplify version control diffs.

The GitHub actions runs these scripts following the YAML files in `.github/workflows`.  The scripts run in the order listed on every user push.
