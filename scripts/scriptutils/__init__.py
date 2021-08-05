import os
import glob
import csv
import git
import logging
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

# This is the configuration for parsing parts sheets
SHEET_CONFIG = {
    'basic_sheet': 'Parts and Devices',
    'basic_parts_name': 'B1',
    'basic_parts_description': 'A5',
    'basic_first_row': 15,

    'composite_sheet': 'Libraries and Composites',
    'composite_parts_name': None,
    'composite_parts_description': None,
    'composite_first_row': 24,
    'composite_strain_col': None,
    'composite_context_col': 4,
    'composite_constraints_col': 5
}

# TODO: rewrite into remappable IDs after the model of identifiers.org/pypi
DISTRIBUTION_NAMESPACE = 'https://github.com/iGEM-Engineering/iGEM-distribution'


def package_stem(package) -> str:
    local = urllib.parse.quote(os.path.basename(package),safe='')
    return f'{DISTRIBUTION_NAMESPACE}/{local}'


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
        logging.error(f' Could not find package excel file')
    elif len(excel_files) > 1:
        logging.error(f' Found multiple Excel files in package: {excel_files}')
    else:
        return os.path.join(directory, excel_files[0])


def regularize_directories():
    """Ensure that each package has an export directory and no other subdirectories and precisely one package Excel file
    """
    dirs = package_dirs()
    print(f'Scanning; found {len(dirs)} packages')
    for d in dirs:
        print(f'Scanning package {d}')

        # Check that there is exactly one subdirectory
        sub_dirs = [s for s in os.scandir(d) if s.is_dir()]
        if len(sub_dirs) == 0:
            os.mkdir(os.path.join(d, EXPORT_DIRECTORY))
            print(f' Created missing export directory {EXPORT_DIRECTORY}')
        elif len(sub_dirs) == 1:
            if not sub_dirs[0].name == EXPORT_DIRECTORY:
                logging.error(f' Found unexpected subdirectory: {sub_dirs[0]}')
        else:  # more than one
            logging.error(
                f' Found unexpected subdirectories: {(s.name for s in sub_dirs if not s.name == EXPORT_DIRECTORY)}')

        # Confirm that package excel file can be located
        package_excel(d)


def export_csvs(package: str):
    """Export a package Excel file into CSVs

    Parameters
    ----------
    package: directory for Excel file
    """
    # Get the package excel file
    excel_file = package_excel(package)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)  # filter the "data validation not supported" warning
        wb = openpyxl.open(excel_file, data_only=True)

    # Target directory name:
    target_directory = os.path.join(package, EXPORT_DIRECTORY)

    # Clear out any old CSV exports
    for old_csv in glob.glob(os.path.join(target_directory, '*.csv')):
        print(f' Removing old CSV export {os.path.basename(old_csv)}')
        os.remove(old_csv)

    # Export the target sheets
    for n in EXPORT_SHEETS:
        sh = wb[n]
        export_file = os.path.join(target_directory, f'{n}.csv')
        with open(export_file, 'w') as f:
            print(f' Writing sheet as CSV {f.name}')
            c = csv.writer(f)
            for r in sh.rows:
                c.writerow([cell.value for cell in r])


def export_sbol(package: str) -> sbol3.Document:
    """Export a package Excel file into SBOL

    Parameters
    ----------
    package: directory for Excel file
    Returns
    ----------
    Document that has been written
    """
    # get workbook and perform conversion
    excel_file = package_excel(package)
    sbol3.set_namespace(package_stem(package))  # TODO: update after resolution of https://github.com/SynBioDex/pySBOL3/issues/288
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)  # filter the "data validation not supported" warning
        wb = openpyxl.open(excel_file, data_only=True)
    doc = excel_to_sbol(wb, SHEET_CONFIG)
    # write into the target directory
    target_name = os.path.join(package, EXPORT_DIRECTORY, SBOL_EXPORT_NAME)
    doc.write(target_name, sbol3.SORTED_NTRIPLES)
    return doc
