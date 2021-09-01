import os
import sys
import git
import sbol3

import scriptutils
import sbol_utilities.expand_combinatorial_derivations
from sbol_utilities.helper_functions import flatten

error = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Expanding package build plan {os.path.basename(p)}')
    try:
        scriptutils.expand_build_plan(p)

    except (OSError, ValueError) as e:
        print(f'Could not compute build plan for {os.path.basename(p)}: {e}')
        error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)
