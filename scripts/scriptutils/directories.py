import os
import glob
import csv
import git
import warnings
import urllib.parse
import openpyxl
from sbol_utilities.excel_to_sbol import excel_to_sbol
import sbol3

# This is the export directory into which sheets and other products will be placed
EXPORT_DIRECTORY = 'views'
# These are the sheets to export, which will be written as CSVs with the same name:
EXPORT_SHEETS = ['Parts and Devices', 'Libraries and Composites']
# Name of the base SBOL export name (not filled in with details)
SBOL_EXPORT_NAME = 'package_specification.nt'


def package_dirs() -> list[str]:
    """Find all packages in the repository

    Returns
    -------
    List of package directory path names
    """
    root = git.Repo('.', search_parent_directories=True).working_tree_dir
    exclusions = {'scripts'}
    return [d.path for d in os.scandir(root) if d.is_dir() and not (d.name in exclusions or d.name.startswith('.'))]


def package_excel(directory) -> str:
    """Check that there is exactly one excel package file (ignoring temp-files)

    Returns
    -------
    Path to package Excel file
    """
    excel_files = [f for f in map(os.path.basename, glob.glob(os.path.join(directory, '*.xlsx')))
                   if not f.startswith('~$')]
    if len(excel_files) == 0:
        raise ValueError(f' Could not find package excel file')
    elif len(excel_files) > 1:
        raise ValueError(f' Found multiple Excel files in package: {excel_files}')
    else:
        return os.path.join(directory, excel_files[0])


def regularize_directory(dir: str):
    """Ensure that a package has one export directory, no other subdirectories, and precisely one package Excel file
    """
    # Check that there is exactly one subdirectory
    sub_dirs = [s for s in os.scandir(dir) if s.is_dir()]
    if len(sub_dirs) == 0:
        os.mkdir(os.path.join(dir, EXPORT_DIRECTORY))
        print(f' Created missing export directory {EXPORT_DIRECTORY}')
    elif len(sub_dirs) == 1:
        if not sub_dirs[0].name == EXPORT_DIRECTORY:
            raise ValueError(f' Found unexpected subdirectory: {sub_dirs[0]}')
    else:  # more than one
        raise ValueError(
            f' Found unexpected subdirectories: {"".join(s.name for s in sub_dirs if not s.name == EXPORT_DIRECTORY)}')

    # Confirm that package excel file can be located
    package_excel(dir)
