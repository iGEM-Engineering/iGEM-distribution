import os
import scriptutils

if __name__ == '__main__':
    packages = scriptutils.regularize_directories.package_dirs()
    for p in packages:
        print(f'Exporting CSVs for package {os.path.basename(p)}')
        try:
            scriptutils.export_csvs(p)
        except OSError as e:
            print(f'Could not export CSV files for package {p}: {e}')
