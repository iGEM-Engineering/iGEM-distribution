import os

import sbol3

import scriptutils


SBOL2_RDF_XML = 'iGEM_SBOL2_imports.xml'
SBOL3_SORTED_NT = 'iGEM_SBOL3_imports.nt'


def convert2to3(pkg_dir):
    sbol2_path = os.path.join(pkg_dir, SBOL2_RDF_XML)
    sbol3_path = os.path.join(pkg_dir, SBOL3_SORTED_NT)
    scriptutils.convert2to3(sbol2_path, sbol3_path, sbol3.SORTED_NTRIPLES)
    return sbol3_path


for p in scriptutils.package_dirs():
    print(f'Converting SBOL2 to SBOL3 for package {os.path.basename(p)}')
    outfile = convert2to3(p)
    print(f'Wrote {outfile}')
