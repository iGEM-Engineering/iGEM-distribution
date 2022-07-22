''' Export SBOL files for packages '''

import os
import sys
import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:
    print(f'Exporting SBOL from Excel for package {os.path.basename(p)}')
    try:
        doc = scriptutils.export_sbol(p)
        print(f'  {len(doc.objects)} designs and collections exported')
    except (OSError, ValueError) as e:
        print(f'Could not export SBOL file for package {os.path.basename(p)}: {e}')
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
