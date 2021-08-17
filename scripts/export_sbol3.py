import os
import subprocess
import sys

import sbol3

import scriptutils


SBOL_CONVERTER = 'scripts/sbol'
SBOL2_RDF_XML = 'iGEM_SBOL2_imports.xml'
SBOL3_SORTED_NT = 'iGEM_SBOL3_imports.nt'


def convert2to3(pkg_dir):
    sbol2_path = os.path.join(pkg_dir, SBOL2_RDF_XML)
    sbol3_path = os.path.join(pkg_dir, SBOL3_SORTED_NT)
    cmd = [SBOL_CONVERTER, '-output', 'sbol3',
           'import', sbol2_path,
           'convert', '--target-sbol-version', '3']
    # This will raise and exception if the command fails
    proc = subprocess.run(cmd, capture_output=True, check=True)
    # Now convert the RDF-XML to Sorted N-Triples
    doc = sbol3.Document()
    doc.read_string(proc.stdout.decode('utf-8'), sbol3.RDF_XML)
    doc.write(sbol3_path, sbol3.SORTED_NT)
    return sbol3_path


for p in scriptutils.package_dirs():
    print(f'Converting SBOL2 to SBOL3 for package {os.path.basename(p)}')
    outfile = convert2to3(p)
    print(f'Wrote {outfile}')
