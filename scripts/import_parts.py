''' Import parts for packages '''

import os
import sys
import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:
    print(f'Importing parts for package {os.path.basename(p)}')
    scriptutils.import_parts(p)

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
