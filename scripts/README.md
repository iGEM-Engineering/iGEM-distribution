# Scripts

This directory contains scripts that automatically collect, generate, or validate materials in the repository.
These scripts run in sequential stages: 

1. Check package structure and export from Excel files
    1. `regularize_directories.py` ensures that packages directories are non-nested, that there is one Excel file per package directory, and that every package directory has a `views` subdirectory for storing generated artifacts.
    2. `export_csvs.py` exports a CSV from each user tab of a package Excel file into the corresponding `views` directory, in order to simplify version control diffs.
    3. `export_sbol.py` exports an SBOL specification for the package from the package Excel file into the corresponding `views` directory. This contains all of the information in the Excel file, but is not yet fused with information from imported parts.
2. Retrieve missing parts
    1. `import_parts.py` scans package Excel files and the genetic design files in the package directory to see what parts are missing definitions. If there are missing parts with source references that the script knows how to interpret, it attempts to download them. Currently supports retrieval from NCBI and the iGEM Registry.
    2. `convert_sbol_2to3.py` changes all SBOL2 imports into SBOL3 imports that are more compatible with version control.
3. Build and validate final packages
    1. `collate_packages.py` combines a package specification and genetic design files to produce a unified SBOL file in `views`
    2. `expand_combinations.py` produces a build plan for each package and saves it into the unified package SBOL file
    3. `generate_markdown.py` generates README files summarizing each package
4. Build the distribution
    1. `build_distribution.py` combines all of the packages into a single distribution file in the root directory, generates a summary README file, and exports GenBank for inspection and FASTA for synthesis.

The GitHub actions runs these scripts following the YAML files in `.github/workflows`.  The scripts run in the order listed on every user push.

# SBOL Converter

The SBOL converter, `sbol`, is
[Release 10](https://github.com/sboltools/sboltools/releases/tag/release-10)
of [sboltools](https://github.com/sboltools/sboltools). It is
captured here to provide a stable dependency.

# Troubleshooting 

## Dependencies

- SBOL requires both Node and Java installed, else specific tests will fail.

### Ubuntu 22.04 LTS
- SBOL requires biopython to be installed, will require:
    ```bash 
    sudo apt-get install python3-dev
    sudo apt-get install build-essential
    ```