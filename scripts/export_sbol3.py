import os
import subprocess
import sys

import scriptutils


SBOL_CONVERTER = 'scripts/sbol'
SBOL2_RDF_XML = 'iGEM_SBOL2_imports.xml'
SBOL3_RDF_XML = 'iGEM_SBOL3_imports.xml'
SBOL3_SORTED_NT = 'iGEM_SBOL3_imports.nt'


def convert2to3(pkg_dir):
    sbol2_path = os.path.join(pkg_dir, SBOL2_RDF_XML)
    sbol3_path = os.path.join(pkg_dir, SBOL3_RDF_XML)
    cmd = [SBOL_CONVERTER, '-output', 'sbol3',
           'import', sbol2_path,
           'convert', '--target-sbol-version', '3']
    with open(sbol3_path, 'w') as fp:
        result = subprocess.check_call(cmd, stdout=fp)
    return sbol3_path


for p in scriptutils.package_dirs():
    print(f'Converting SBOL2 to SBOL3 for package {os.path.basename(p)}')
    outfile = convert2to3(p)
    print(f'Wrote {outfile}')
