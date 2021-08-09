import os
import sys
import scriptutils

error = False
packages = scriptutils.package_dirs()
for p in packages:
    print(f'Importing parts for package {os.path.basename(p)}')
    scriptutils.import_parts(p)

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)
