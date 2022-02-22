''' Collate packages '''

import os
import sys

import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Collating specification and imports into complete package {os.path.basename(p)}')
    try:
        scriptutils.collate_package(p)

    except (OSError, ValueError) as e:
        print(f'Could not collate package {os.path.basename(p)}: {e}')
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
