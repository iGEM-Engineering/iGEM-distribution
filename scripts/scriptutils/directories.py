import os
import glob
import warnings
from typing import List, Union
from copy import copy

import git
import openpyxl
import sbol3

EXPORT_DIRECTORY = 'views'
"""Export directory into which sheets and other products will be placed"""
EXPORT_SHEETS = ['Parts and Devices', 'Libraries and Composites']
"""List of sheets to export, which will be written as CSVs with the same name"""
SBOL_EXPORT_NAME = 'package_specification.nt'
"""Name of the base SBOL3 export name (not filled in with details)"""
SBOL_PACKAGE_NAME = 'package.nt'
"""Name of the fully assembled SBOL3 package"""

DISTRIBUTION_NAME = 'distribution.nt'
"""File name for the distribution as a whole, to be located in the root directory"""
DISTRIBUTION_FASTA = 'distribution_synthesis_inserts.fasta'
"""File name for the distribution FASTA export for synthesis, to be located in the root directory"""
DISTRIBUTION_GENBANK = 'distribution.gb'
"""File name for the distribution GenBank export for synthesis/review, to be located in the root directory"""


def distribution_dir() -> str:
    """Returns the root directory for the distribution.

    :return: Path for distribution directory
    """
    root = git.Repo('.', search_parent_directories=True).working_tree_dir
    return root

def package_dirs() -> List[str]:
    """Find all packages in the repository

    Returns
    -------
    List of package directory path names
    """
    root = git.Repo('.', search_parent_directories=True).working_tree_dir
    exclusions = {'scripts', 'docs'}
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


def copy_sheets_to_packages(sheets: Union[str,list[str]], template: str = None) -> None:
    """Copy designated sheets from template to all package Excel files.
    This is intended to be used for updating the non-user-edited sheets

    :param sheets: list of sheet names to copy, or a single name that will be listified
    :param template: path to template file; defaults to 'package template.xlsx' in root
    """
    # set template to default if unspecified
    if template is None:
        root = git.Repo('.', search_parent_directories=True).working_tree_dir
        template = os.path.join(root, 'package template.xlsx')
    if isinstance(sheets,str):
        sheets = [sheets]

    # open template file and check that all sheets are there
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)  # filter the "data validation not supported" warning
        template_excel = openpyxl.open(template, data_only=True)
    for s in sheets:
        template_excel[s]  # KeyError will be thrown if any sheet doesn't exist

    # for each package
    for package in package_dirs():
        # open the package excel file
        package_excel_file = package_excel(package)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)  # filter the "data validation not supported" warning
            target_excel = openpyxl.open(package_excel_file, data_only=True)

        # copy the sheets
        print(f'Copying sheets to {package_excel_file}')
        for s in sheets:
            print(f'  Copying sheet "{s}"')
            target_index = target_excel.index(target_excel[s])
            # remove old sheet, create a blank, then copy values
            target_excel.remove_sheet(target_excel[s])
            target_excel.create_sheet(s,target_index)
            copy_sheet(template_excel[s], target_excel[s])

        # save
        target_excel.save(package_excel_file)
        print(f'  Saved after copying all sheets')


###############
## Copy a sheet with style, format, layout, etc. from one Excel file to another Excel file
## Adapted from https://stackoverflow.com/a/68800310/2779147


def copy_sheet(source_sheet, target_sheet):
    copy_cells(source_sheet, target_sheet)  # copy all the cell values and styles
    copy_sheet_attributes(source_sheet, target_sheet)

def copy_sheet_attributes(source_sheet, target_sheet):
    target_sheet.sheet_format = copy(source_sheet.sheet_format)
    target_sheet.sheet_properties = copy(source_sheet.sheet_properties)
    target_sheet.merged_cells = copy(source_sheet.merged_cells)
    target_sheet.page_margins = copy(source_sheet.page_margins)
    target_sheet.freeze_panes = copy(source_sheet.freeze_panes)

    # set row dimensions
    # So you cannot copy the row_dimensions attribute. Does not work (because of meta data in the attribute I think). So we copy every row's row_dimensions. That seems to work.
    for rn in range(len(source_sheet.row_dimensions)):
        target_sheet.row_dimensions[rn] = copy(source_sheet.row_dimensions[rn])

    if source_sheet.sheet_format.defaultColWidth is None:
        print('Unable to copy default column wide')
    else:
        target_sheet.sheet_format.defaultColWidth = copy(source_sheet.sheet_format.defaultColWidth)

    # set specific column width and hidden property
    # we cannot copy the entire column_dimensions attribute so we copy selected attributes
    for key, value in source_sheet.column_dimensions.items():
        target_sheet.column_dimensions[key].min = copy(source_sheet.column_dimensions[key].min)   # Excel actually groups multiple columns under 1 key. Use the min max attribute to also group the columns in the targetSheet
        target_sheet.column_dimensions[key].max = copy(source_sheet.column_dimensions[key].max)  # https://stackoverflow.com/questions/36417278/openpyxl-can-not-read-consecutive-hidden-columns discussed the issue. Note that this is also the case for the width, not onl;y the hidden property
        target_sheet.column_dimensions[key].width = copy(source_sheet.column_dimensions[key].width) # set width for every column
        target_sheet.column_dimensions[key].hidden = copy(source_sheet.column_dimensions[key].hidden)


def copy_cells(source_sheet, target_sheet):
    for (row, col), source_cell in source_sheet._cells.items():
        target_cell = target_sheet.cell(column=col, row=row)

        target_cell._value = source_cell._value
        target_cell.data_type = source_cell.data_type

        if source_cell.has_style:
            target_cell.font = copy(source_cell.font)
            target_cell.border = copy(source_cell.border)
            target_cell.fill = copy(source_cell.fill)
            target_cell.number_format = copy(source_cell.number_format)
            target_cell.protection = copy(source_cell.protection)
            target_cell.alignment = copy(source_cell.alignment)

        if source_cell.hyperlink:
            target_cell._hyperlink = copy(source_cell.hyperlink)

        if source_cell.comment:
            target_cell.comment = copy(source_cell.comment)

