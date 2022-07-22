''' Check packages structure '''

import os
import sys
import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
print(f'Scanning; found {len(packages)} packages')
for p in packages:
    print(f'Scanning package {p}')
    try:
        scriptutils.regularize_directory(p)
    except ValueError as e:
        print(f'Bad structure for package {os.path.basename(p)}: {e}')
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
