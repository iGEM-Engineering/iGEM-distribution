import subprocess
import glob
import os

import rdflib
import sbol2
import sbol3
from sbol_utilities.helper_functions import flatten, strip_sbol2_version
from .part_retrieval import extensions

# sbol javascript executable based on https://github.com/sboltools/sbolgraph
# Location: scripts/sbol
SBOL_CONVERTER = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'sbol')


def convert_identities2to3(sbol3_data: str) -> str:
    """Convert SBOL2 identities into SBOL3 identities.

    Takes RDF-XML data as a string, converts all SBOL2 identities into
    SBOL3 identities, and returns RDF-XML as a string.
    """
    # Convert the /[version] identities of SBOL2 into identities for SBOL3
    g = rdflib.Graph().parse(data=sbol3_data)
    subjects = sorted(list(set(g.subjects())))
    for old_identity in subjects:
        # Check if the identity needs to change:
        new_identity = rdflib.URIRef(strip_sbol2_version(old_identity))
        if new_identity == old_identity:
            continue

        # Verify that s has a rdflib.RDF.type in the sbol3 namespace
        sbol3_type_count = 0
        for o in g.objects(old_identity, rdflib.RDF.type):
            if o.startswith(sbol3.SBOL3_NS):
                sbol3_type_count += 1
        if sbol3_type_count < 1:
            # Not an SBOL object, so don't rename it
            continue

        # Update all triples where old_identity is the subject
        for s, p, o in g.triples((old_identity, None, None)):
            g.add((new_identity, p, o))
            g.remove((s, p, o))
        # Update all triples where old_identity is the object
        for s, p, o in g.triples((None, None, old_identity)):
            g.add((s, p, new_identity))
            g.remove((s, p, o))
    return g.serialize(format="xml")


def convert2to3(sbol2_path: str) -> sbol3.Document:
    cmd = [SBOL_CONVERTER, '-output', 'sbol3',
           'import', sbol2_path,
           'convert', '--target-sbol-version', '3']
    # This will raise an exception if the command fails
    proc = subprocess.run(cmd, capture_output=True, check=True)
    # Extract the rdf_xml output from the sbol converter
    rdf_xml = proc.stdout.decode('utf-8')
    # Post-process the conversion by updating object identities
    rdf_xml = convert_identities2to3(rdf_xml)
    doc = sbol3.Document()
    doc.read_string(rdf_xml, sbol3.RDF_XML)
    return doc


def convert_package_sbol2_files(package: str) -> dict[str, str]:
    """Find all SBOL2 import files in a package directory and convert them to SBOL3 sorted n-triples

    :param package: path of package to search
    :return: dictionary mapping paths of SBOL2 inputs to SBOL3 outputs
    """
    mappings = {}

    # import SBOL2
    for file in flatten(glob.glob(os.path.join(package, ext)) for ext in extensions['SBOL2']):
        print(f'Attempting to convert SBOL2 file {file}')
        file3 = os.path.splitext(file)[0]+'.nt'  # make an SBOL3 version of the file name
        doc2 = sbol2.Document()
        doc2.read(file)  # confirm that it is, in fact, an SBOL2 file
        doc3 = convert2to3(file)
        print(f'Writing converted SBOL3 file to {file3}')
        doc3.write(file3, sbol3.SORTED_NTRIPLES)
        # record the conversion for later use
        mappings[file] = file3

    return mappings
