import os
import glob
import csv
import warnings
import urllib.parse
import openpyxl
from sbol_utilities.excel_to_sbol import excel_to_sbol
import sbol3

from .directories import package_excel, EXPORT_DIRECTORY, SBOL_EXPORT_NAME, EXPORT_SHEETS

# This is the configuration for parsing parts sheets
SHEET_CONFIG = {
    'basic_sheet': 'Parts and Devices',
    'basic_parts_name': 'B1',
    'basic_parts_description': 'A5',
    'basic_first_row': 15,

    'composite_sheet': 'Libraries and Composites',
    'composite_parts_name': None,
    'composite_parts_description': None,
    'composite_first_row': 14,
    'composite_strain_col': None,
    'composite_context_col': 4,
    'composite_constraints_col': 5,
    'composite_first_part_col': 6
}

# TODO: rewrite into remappable IDs after the model of identifiers.org/pypi
DISTRIBUTION_NAMESPACE = 'https://github.com/iGEM-Engineering/iGEM-distribution'


def package_stem(package) -> str:
    local = urllib.parse.quote(os.path.basename(package), safe='')
    return f'{DISTRIBUTION_NAMESPACE}/{local}'


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
    sbol3.set_namespace(package_stem(package))  # TODO: update after resolution of https://github.com/SynBioDex/pySBOL3/issues/288 # pylint: disable=C0301 # noqa: E501

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)  # filter the "data validation not supported" warning
        wb = openpyxl.open(excel_file, data_only=True)
    doc = excel_to_sbol(wb, SHEET_CONFIG)
    # write into the target directory
    target_name = os.path.join(package, EXPORT_DIRECTORY, SBOL_EXPORT_NAME)
    doc.write(target_name, sbol3.SORTED_NTRIPLES)
    return doc
