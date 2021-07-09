import os
import glob
import openpyxl
import regularize_directories
import csv

# These are the sheets to export, which will be written as CSVs with the same name:
EXPORT_SHEETS = ['Basic Parts', 'Libraries and Composites']

packages = regularize_directories.package_dirs()
for p in packages:
    # logging.log(logging.INFO, f'Exporting CSVs for package {os.path.basename(p)}')
    print(f'Exporting CSVs for package {os.path.basename(p)}')
    try:
        # Get the package excel file
        excel_file = regularize_directories.package_excel(p)
        wb = openpyxl.open(excel_file, data_only=True)

        # Target directory name:
        target_directory = os.path.join(p, regularize_directories.EXPORT_DIRECTORY)

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

    except OSError as e:
        print(f'Could not export CSV files for package {p}: {e}')
