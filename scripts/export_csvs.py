import os
import sys
import scriptutils

error = False
packages = scriptutils.package_dirs()
for p in packages:
    print(f'Exporting CSVs for package {os.path.basename(p)}')
    try:
        scriptutils.export_csvs(p)
    except OSError as e:
        print(f'Could not export CSV files for package {os.path.basename(p)}: {e}')
        error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)
