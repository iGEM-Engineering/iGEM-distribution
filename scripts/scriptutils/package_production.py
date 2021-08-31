import os

import rdflib
import sbol3
from sbol_utilities.expand_combinatorial_derivations import root_combinatorial_derivations, expand_derivations
from sbol_utilities.helper_functions import flatten

from .part_retrieval import package_parts_inventory
from .directories import EXPORT_DIRECTORY, SBOL_EXPORT_NAME, SBOL_PACKAGE_NAME
from .package_specification import package_stem


BUILD_PRODUCTS_COLLECTION = 'BuildProducts'


def collate_package(package: str) -> None:
    """Given a package specification and an inventory of parts, unify them into a complete SBOL3 package & write it out

    :param package: path of package to search
    :return: None: would return document, except that rewriting requires change to RDF graph
    """
    # read the package specification
    print(f'Collating materials for package {package}')
    spec_name = os.path.join(package, EXPORT_DIRECTORY, SBOL_EXPORT_NAME)
    doc = sbol3.Document()
    doc.read(spec_name, sbol3.SORTED_NTRIPLES)

    # collect the inventory
    inventory = package_parts_inventory(package)

    # search old object for aliases; if found, remove and add to rewriting plan
    print(f'aliases: {inventory.aliases}')
    print(f'identifies: {[o.identity for o in doc.objects]}')
    to_remove = [o for o in doc.objects if o.identity in inventory.aliases]
    print(f'  Removing {len(to_remove)} objects to be replaced by imports')
    print(f'Removal list: {[o.identity for o in to_remove]}')
    for o in to_remove:
        doc.objects.remove(o)

    # copy the contents of each file into the main document
    for f in inventory.files:
        import_doc = f.get_sbol3_doc()
        print(f'  Importing {len(import_doc.objects)} objects from file {f.path}')
        for o in import_doc.objects:
            if o.identity in (o.identity for o in doc.objects):
                continue  # TODO: add a more principled way of handling duplicates
            o.copy(doc)
            # TODO: figure out how to merge information from Excel specs

    # TODO: remove graph workaround on resolution of https://github.com/SynBioDex/pySBOL3/issues/207
    # Change to a graph in order to rewrite identities:
    g = doc.graph()
    rewriting_plan = {o.identity: inventory.aliases[o.identity]
                      for o in to_remove if inventory.aliases[o.identity] != o.identity}
    print(f'  Rewriting {len(rewriting_plan)} objects to their aliases: {rewriting_plan}')
    for old_identity, new_identity in rewriting_plan.items():
        # Update all triples where old_identity is the object
        for s, p, o in g.triples((None, None, rdflib.URIRef(old_identity))):
            g.add((s, p, rdflib.URIRef(new_identity)))
            g.remove((s, p, o))

    # write composite file into the target directory
    target_name = os.path.join(package, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
    print(f'  Writing collated document to {target_name}')
    # TODO: code taken from pySBOL3 until resolution of https://github.com/SynBioDex/pySBOL3/issues/207
    nt_text = g.serialize(format=sbol3.NTRIPLES)
    lines = nt_text.splitlines(keepends=True)
    lines.sort()
    serialized = b''.join(lines).decode()
    with open(target_name, 'w') as outfile:
        outfile.write(serialized)


def expand_build_plan(package: str) -> sbol3.Document:
    """Expand the build plans (libraries & composites sheet) in a package's collated SBOL3 Document

    :param package: path of package to operate on
    :return: Updated document
    """
    path = os.path.join(package, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
    doc = sbol3.Document()
    doc.read(path)
    # Add a build plan collection that contains all of the expanded derivations
    roots = list(root_combinatorial_derivations(doc))
    # TODO: change namespace handling after resolution of https://github.com/SynBioDex/pySBOL3/issues/288
    sbol3.set_namespace(package_stem(package))
    derivative_collections = expand_derivations(roots)
    doc.add(sbol3.Collection(BUILD_PRODUCTS_COLLECTION, members=flatten(c.members for c in derivative_collections)))
    # Make sure the document is valid
    report = doc.validate()
    if len(report):
        raise ValueError(report)
    # Write in place and return
    doc.write(path,sbol3.SORTED_NTRIPLES)
    return doc
