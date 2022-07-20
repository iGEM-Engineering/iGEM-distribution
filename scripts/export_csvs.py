""" Export CSV files for packages """

import os
import sys
import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:
    print(f"Exporting CSVs for package {os.path.basename(p)}")
    try:
        scriptutils.export_csvs(p)
    except OSError as e:
        print(f"Could not export CSV files for package {os.path.basename(p)}: {e}")
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
