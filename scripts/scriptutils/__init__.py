import openpyxl
import os
import glob
import csv
import git
import logging


# This is the export directory into which sheets and other products will be placed
EXPORT_DIRECTORY = 'views'
# These are the sheets to export, which will be written as CSVs with the same name:
EXPORT_SHEETS = ['Parts and Devices', 'Libraries and Composites']


def package_dirs():
    root = git.Repo('.', search_parent_directories=True).working_tree_dir
    exclusions = {'scripts'}
    return [d for d in os.scandir(root) if d.is_dir() and not (d.name in exclusions or d.name.startswith('.'))]


def package_excel(directory):
    # Check that there is exactly one excel package file (ignoring temp-files)
    excel_files = [f for f in map(os.path.basename, glob.glob(os.path.join(directory, '*.xlsx')))
                   if not f.startswith('~$')]
    if len(excel_files) == 0:
        logging.error(f' Could not find package excel file')
    elif len(excel_files) > 1:
        logging.error(f' Found multiple Excel files in package: {excel_files}')
    else:
        return os.path.join(directory, excel_files[0])


def regularize_directories():
    dirs = package_dirs()
    print(f'Scanning; found {len(dirs)} packages')
    for d in dirs:
        print(f'Scanning package {d.name}')

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
    # Get the package excel file
    excel_file = package_excel(package)
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
