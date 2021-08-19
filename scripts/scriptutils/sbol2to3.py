import rdflib
import sbol3


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
            continue
        elif sbol3_type_count > 1:
            # Isn't this an error?
            print('SBOL3 type count is %d (more than one) for %r'
                  % (sbol3_type_count, old_identity))
            continue
        # Update all triples where s is the subject
        new_identity = rdflib.URIRef(old_identity[:-2])
        for s2, p2, o2 in g.triples((old_identity, None, None)):
            g.add((new_identity, p2, o2))
            g.remove((s2, p2, o2))
        # Update all triples where s is the object
        for s, p, o in g.triples((None, None, old_identity)):
            g.add((s, p, new_identity))
            g.remove((s, p, o))
    return g.serialize(format="xml")
