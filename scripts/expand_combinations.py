''' Compute build plan for packages '''

import os
import sys

import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Expanding package build plan {os.path.basename(p)}')
    try:
        scriptutils.expand_build_plan(p)

    except (OSError, ValueError) as e:
        print(f'Could not compute build plan for {os.path.basename(p)}: {e}')
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
