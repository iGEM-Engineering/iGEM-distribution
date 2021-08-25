# Scripts

This directory contains scripts that automatically collect, generate, or validate materials in the repository.

* `regularize_directories.py` ensures that packages directories are non-nested, that there is one Excel file per package directory, and that every package directory has a `views` subdirectory for storing generated artifacts.
* `export_csvs.py` exports a CSV from each user tab of a package Excel file into the corresponding `views` directory, in order to simplify version control diffs.
* `export_sbol.py` exports an SBOL specification for the package from the package Excel file into the corresponding `views` directory. This contains all of the information in the Excel file, but is not yet fused with information from imported parts.
* `import_basic_parts.py` scans package Excel files and the genetic design files in the package directory to see what parts are missing definitions. If there are missing parts with source references that the script knows how to interpret, it attempts to download them. Currently supports retrieval from NCBI and the iGEM Registry.

The GitHub actions runs these scripts following the YAML files in `.github/workflows`.  The scripts run in the order listed on every user push.

# SBOL Converter

The SBOL converter, `sbol`, is
[Release 10](https://github.com/sboltools/sboltools/releases/tag/release-10)
of [sboltools](https://github.com/sboltools/sboltools). It is
captured here to provide a stable dependency.
