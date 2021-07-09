import glob
import logging
import os
import git

EXPORT_DIRECTORY = 'views'


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


def __main__():
    for d in package_dirs():
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
