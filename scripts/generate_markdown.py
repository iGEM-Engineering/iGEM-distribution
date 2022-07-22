""" Generates README for package"""
import os
import sys
import sbol3

import scriptutils

ERROR = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Generating README for package {os.path.basename(p)}')
    try:
        doc = sbol3.Document()
        doc.read(os.path.join(p, scriptutils.EXPORT_DIRECTORY, scriptutils.SBOL_PACKAGE_NAME))
        scriptutils.generate_package_summary(p, doc)

    except (OSError, ValueError) as e:
        print(f'Could not generate README for package {os.path.basename(p)}: {e}')
        ERROR = True

# If there was an error, flag on exit in order to notify executing YAML script
if ERROR:
    sys.exit(1)
