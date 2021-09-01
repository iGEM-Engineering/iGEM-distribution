import logging
import os

import rdflib
import sbol3
from sbol_utilities.expand_combinatorial_derivations import root_combinatorial_derivations, expand_derivations
from sbol_utilities.helper_functions import flatten

from .part_retrieval import package_parts_inventory
from .directories import EXPORT_DIRECTORY, SBOL_EXPORT_NAME, SBOL_PACKAGE_NAME, DISTRIBUTION_NAME
from .package_specification import package_stem, DISTRIBUTION_NAMESPACE

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
    to_remove = [o for o in doc.objects if o.identity in inventory.aliases]
    print(f'  Removing {len(to_remove)} objects to be replaced by imports')
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
    if roots:
        derivative_collections = expand_derivations(roots)
        doc.add(sbol3.Collection(BUILD_PRODUCTS_COLLECTION, members=flatten(c.members for c in derivative_collections)))
    else:
        logging.warning(f'No samples specified be built in package {package}')
        doc.add(sbol3.Collection(BUILD_PRODUCTS_COLLECTION))
    # Make sure the document is valid
    report = doc.validate()
    if len(report):
        raise ValueError(report)
    # Write in place and return
    doc.write(path,sbol3.SORTED_NTRIPLES)
    return doc


def build_distribution(root: str, packages: list[str]) -> sbol3.Document:
    """Given a package specification and an inventory of parts, unify them into a complete SBOL3 package & write it out

    :param root: location for distribution
    :param packages: list of packages to include in distribution
    :return: document for joint package
    """

    # make a fresh SBOL collection and add a build plan document
    print('Assembling distribution build plan')
    doc = sbol3.Document()
    # TODO: change namespace handling after resolution of https://github.com/SynBioDex/pySBOL3/issues/288
    sbol3.set_namespace(DISTRIBUTION_NAMESPACE)
    build_plan = sbol3.Collection(BUILD_PRODUCTS_COLLECTION)
    doc.add(build_plan)

    complete_build_set = set()

    # copy the materials from every package into it
    for package in packages:
        # get fully-assembled package document
        import_doc = sbol3.Document()
        import_doc.read(os.path.join(package, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))

        # copy over all the objects
        print(f'  Importing {len(import_doc.objects)} objects from package {package}')
        for o in import_doc.objects:
            if o.identity in (o.identity for o in doc.objects):
                continue  # TODO: add a more principled way of handling duplicates
            o.copy(doc)

        # add materials to the members for the build plan
        import_build_plan = import_doc.find(BUILD_PRODUCTS_COLLECTION)
        if not import_build_plan:
            raise ValueError(f'Could not locate build plan for package {package_stem(package)}')
        print(f'  Importing build plan with {len(import_build_plan.members)} samples')
        complete_build_set |= {str(m) for m in import_build_plan.members}

    # set the distribution build plan contents
    print(f'Distribution build plan specifies {len(complete_build_set)} samples')
    build_plan.members = list(complete_build_set)

    # finally, validate and write
    report = doc.validate()
    if len(report):
        raise ValueError(report)
    print(f'Writing distribution plan')
    doc.write(os.path.join(root, DISTRIBUTION_NAME), sbol3.SORTED_NTRIPLES)
    return doc
