import logging
import os
import scriptutils

if __name__ == '__main__':
    dirs = scriptutils.package_dirs()
    print(f'Scanning; found {len(dirs)} packages')
    for d in dirs:
        print(f'Scanning package {d.name}')

        # Check that there is exactly one subdirectory
        sub_dirs = [s for s in os.scandir(d) if s.is_dir()]
        if len(sub_dirs) == 0:
            os.mkdir(os.path.join(d, scriptutils.EXPORT_DIRECTORY))
            print(f' Created missing export directory {scriptutils.EXPORT_DIRECTORY}')
        elif len(sub_dirs) == 1:
            if not sub_dirs[0].name == scriptutils.EXPORT_DIRECTORY:
                logging.error(f' Found unexpected subdirectory: {sub_dirs[0]}')
        else:  # more than one
            logging.error(
                f' Found unexpected subdirectories: {(s.name for s in sub_dirs if not s.name == scriptutils.EXPORT_DIRECTORY)}')

        # Confirm that package excel file can be located
        scriptutils.package_excel(d)
