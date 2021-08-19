import subprocess

import rdflib
import sbol3

SBOL_CONVERTER = 'scripts/sbol'


def convert_identities2to3(sbol3_data: str) -> str:
    """Convert SBOL2 identities into SBOL3 identities.

    Takes RDF-XML data as a string, converts all SBOL2 identities into
    SBOL3 identities, and returns RDF-XML as a string.
    """
    # Convert the /1 identities of SBOL2 into identities for SBOL3
    g = rdflib.Graph().parse(data=sbol3_data)
    subjects = sorted(list(set(g.subjects())))
    for old_identity in subjects:
        if not old_identity.endswith('/1'):
            continue
        # Verify that s has a rdflib.RDF.type in the sbol3 namespace
        sbol3_type_count = 0
        for o in g.objects(old_identity, rdflib.RDF.type):
            if o.startswith(sbol3.SBOL3_NS):
                sbol3_type_count += 1
        if sbol3_type_count < 1:
            # Not an SBOL object, so don't rename it
            continue
        # Form the new identity from the original by lopping off the
        # '/1' suffix
        new_identity = rdflib.URIRef(old_identity[:-2])
        # Update all triples where old_identity is the subject
        for s, p, o in g.triples((old_identity, None, None)):
            g.add((new_identity, p, o))
            g.remove((s, p, o))
        # Update all triples where old_identity is the object
        for s, p, o in g.triples((None, None, old_identity)):
            g.add((s, p, new_identity))
            g.remove((s, p, o))
    return g.serialize(format="xml")


def convert2to3(sbol2_path: str, sbol3_path: str, sbol3_format: str) -> str:
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
    # Now convert the RDF-XML to Sorted N-Triples
    doc.write(sbol3_path, sbol3_format)
    return sbol3_path
