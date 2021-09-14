import logging
import os

import rdflib
import sbol3
from Bio import SeqIO
from Bio.Seq import Seq

from sbol_utilities.expand_combinatorial_derivations import root_combinatorial_derivations, expand_derivations
from sbol_utilities.calculate_sequences import calculate_sequences
from sbol_utilities.helper_functions import flatten
from . import convert_to_genbank

from .part_retrieval import package_parts_inventory
from .directories import EXPORT_DIRECTORY, SBOL_EXPORT_NAME, SBOL_PACKAGE_NAME, DISTRIBUTION_NAME, \
    DISTRIBUTION_GENBANK, DISTRIBUTION_FASTA
from .package_specification import package_stem, DISTRIBUTION_NAMESPACE
from .helpers import vector_to_insert

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
    Also attempt to compute all missing sequences (including those of the build plans)

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
        print(f'Expanded {len(derivative_collections)} collections containing a total of {sum(len(c.members) for c in derivative_collections)} parts')
        doc.add(sbol3.Collection(BUILD_PRODUCTS_COLLECTION, members=flatten(c.members for c in derivative_collections)))
        new_sequences = calculate_sequences(doc)
        print(f'Computed sequences for {len(new_sequences)} components')
    else:
        logging.warning(f'No samples specified be built in package {package}')
        doc.add(sbol3.Collection(BUILD_PRODUCTS_COLLECTION))
    # Make sure the document is valid
    report = doc.validate()
    if len(report):
        raise ValueError(report)
    # Write in place and return
    doc.write(path, sbol3.SORTED_NTRIPLES)
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


def extract_synthesis_files(root: str, doc: sbol3.Document) -> sbol3.Document:
    """Export the products to be built from a package/distribution document as GenBank and FASTA
    Note: FASTA is set up for Twist Synthesis, with the identity of the build product on the sequence of the insert
    FASTA descriptions must be blank, as they will otherwise be munged together with the display_id

    :param root: directory where exports will be placed
    :param doc: document to extract from
    :return: slimmed SBOL3 Document containing only direct materials exported in GenBank
    """
    # get the collection of linear build products - the things to actually be synthesized
    print(f'Exporting files for synthesis')
    build_plan = doc.find(f'{DISTRIBUTION_NAMESPACE}/{BUILD_PRODUCTS_COLLECTION}')
    if not build_plan or not isinstance(build_plan, sbol3.Collection):
        raise ValueError(f'Document does not contain linear products collection "{BUILD_PRODUCTS_COLLECTION}"')

    # identify the full constructs and synthesis targets to be copied
    non_components = [m for m in build_plan.members if not isinstance(m.lookup(), sbol3.Component)]
    if len(non_components):
        raise ValueError(f'Linear products collection should contain only Components: {non_components}')

    full_constructs = [m.lookup() for m in sorted(build_plan.members)]
    inserts = {c: vector_to_insert(c) for c in full_constructs}  # May contain non-vector full_constructs

    # for GenBank export, copy build products to new Document, omitting ones without sequences
    sequence_number_warning = 'Omitting {}: GenBank exports require 1 sequence, but found {}'
    build_doc = sbol3.Document()
    build_plan.copy(build_doc)
    components_copied = set(full_constructs)
    n_genbank_constructs = 0
    for c in full_constructs:
        # if build is missing sequence, warn and skip
        if len(c.sequences) != 1:
            print(sequence_number_warning.format(c.identity, len(c.sequences)))
            continue
        c.copy(build_doc)
        c.sequences[0].lookup().copy(build_doc)
        n_genbank_constructs += 1
        # copy over subcomponents and their sequences too  # TODO: make this work for multi-layer components
        for sub_c in c.features:
            if isinstance(sub_c, sbol3.SubComponent) and sub_c.instance_of.lookup() not in components_copied:
                sub = sub_c.instance_of.lookup()
                components_copied.add(sub)
                # if subcomponent is missing sequence, warn and skip
                if len(sub.sequences) != 1:
                    print(sequence_number_warning.format(sub.identity, len(sub.sequences)))
                    continue
                sub.copy(build_doc)
                sub.sequences[0].lookup().copy(build_doc)
    # export the GenBank
    gb_path = os.path.join(root, DISTRIBUTION_GENBANK)
    convert_to_genbank(build_doc, gb_path)
    print(f'Wrote GenBank export file with {n_genbank_constructs} constructs: {gb_path}')

    # for Twist Synthesis FASTA exports, we need to put the identity of the build product on the sequence of the insert
    # descriptions must be blank, as they will otherwise be munged together with the display_id
    n_fasta_constructs = 0
    fasta_path = os.path.join(root, DISTRIBUTION_FASTA)
    with open(fasta_path, 'w') as out:
        for vector, insert in inserts.items():
            # Find all sequences of nucleic acid type
            na_seqs = [s.lookup() for s in insert.sequences if s.lookup().encoding == sbol3.IUPAC_DNA_ENCODING]
            if len(na_seqs) == 0:  # ignore components with no sequence to serialize
                print(f'Part cannot be synthesized because sequence is missing: {insert.identity}')
            elif len(na_seqs) == 1:  # if there is precisely one sequence, write it to the FASTA w. a blank description
                record = SeqIO.SeqRecord(Seq(na_seqs[0].elements), id=vector.display_id, description='')
                out.write(record.format('fasta'))
                n_fasta_constructs += 1
            else:  # warn about components with ambiguous sequences
                print(f'Part cannot be synthesized because it has multiple sequences: {insert.identity}')
    print(f'Wrote FASTA synthesis file with {n_fasta_constructs} constructs: {fasta_path}')

    return build_doc
