import logging
import subprocess
import glob
import os
import tempfile
import urllib
from typing import Union

import rdflib
import sbol2
import sbol3
from Bio import SeqIO, SeqRecord
from Bio.Seq import Seq

from sbol_utilities.excel_to_sbol import string_to_display_id
from sbol_utilities.helper_functions import flatten, strip_sbol2_version, id_sort
from .directories import extensions

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

    # TODO: remove workaround after conversion errors fixed in https://github.com/sboltools/sbolgraph/issues/14
    # for all objects in the prov namespace, add an SBOL type
    # TODO: likely need to do this for OM namespace too
    for s, p, o in g.triples((None, rdflib.RDF.type, None)):
        if o.startswith(sbol3.PROV_NS):
            if str(o) in {sbol3.PROV_ASSOCIATION, sbol3.PROV_USAGE}:
                g.add((s, p, rdflib.URIRef(sbol3.SBOL_IDENTIFIED)))
            else:
                g.add((s, p, rdflib.URIRef(sbol3.SBOL_TOP_LEVEL)))

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


def convert2to3(sbol2_doc: Union[str, sbol2.Document], namespaces=None) -> sbol3.Document:
    """Convert an SBOL2 document to an equivalent SBOL3 document

    :param sbol2_doc: Document to convert
    :param namespaces: list of URI prefixes to treat as namespaces
    :return: equivalent SBOL3 document
    """
    # if we've started with a Document in memory, write it to a temp file
    if namespaces is None:
        namespaces = []
    if isinstance(sbol2_doc, sbol2.Document):
        sbol2_path = tempfile.mkstemp(suffix='.xml')[1]
        sbol2_doc.write(sbol2_path)
    else:
        sbol2_path = sbol2_doc

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

    # TODO: remove workaround after conversion errors fixed in https://github.com/sboltools/sbolgraph/issues/14
    # add in the missing namespace fields where possible, defaulting otherwise
    needs_namespace = {o for o in doc.objects if o.namespace is None}  # TODO: add check for non-TopLevel? See https://github.com/SynBioDex/pySBOL3/issues/295
    for n in namespaces:
        assignable = {o for o in needs_namespace if o.identity.startswith(n)}
        for a in assignable:
            a.namespace = n
        needs_namespace = needs_namespace - assignable
    for o in needs_namespace:  # if no supplied namespace matches, default to scheme//netloc
        # figure out the server to access from the URL
        p = urllib.parse.urlparse(o.identity)
        server = urllib.parse.urlunparse([p.scheme, p.netloc, '', '', '', ''])
        o.namespace = server
    # infer sequences for locations:
    for s in (o for o in doc.objects if isinstance(o, sbol3.Component)):
        if len(s.sequences) != 1:  # can only infer sequences if there is precisely one
            continue
        for f in (f for f in s.features if isinstance(f, sbol3.SequenceFeature) or isinstance(f, sbol3.SubComponent)):
            for loc in f.locations:
                loc.sequence = s.sequences[0]
    # remap sequence encodings:
    encoding_remapping = {
        'http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html': 'https://identifiers.org/edam:format_1207',
        'http://www.chem.qmul.ac.uk/iupac/AminoAcid/': 'https://identifiers.org/edam:format_1208',
        'http://www.opensmiles.org/opensmiles.html': 'https://identifiers.org/edam:format_1196'
    }
    for s in (o for o in doc.objects if isinstance(o, sbol3.Sequence)):
        if s.encoding in encoding_remapping:
            s.encoding = encoding_remapping[s.encoding]
    return doc


def convert_package_sbol2_files(package: str) -> dict[str, str]:
    """Find all SBOL2 import files in a package directory and convert them to SBOL3 sorted n-triples

    :param package: path of package to search
    :return: dictionary mapping paths of SBOL2 inputs to SBOL3 outputs
    """
    mappings = {}

    # import SBOL2
    for file in flatten(glob.glob(os.path.join(package, f'*{ext}')) for ext in extensions['SBOL2']):
        print(f'Attempting to convert SBOL2 file {file}')
        file3 = os.path.splitext(file)[0]+'.nt'  # make an SBOL3 version of the file name
        doc2 = sbol2.Document()
        doc2.read(file)  # confirm that it is, in fact, an SBOL2 file
        doc3 = convert2to3(file)
        # check if it's valid before writing
        report = doc3.validate()
        if len(report.errors) > 0:
            logging.warning('Conversion failed: SBOL3 file has errors')
            for issue in report.errors:
                logging.warning(issue)
            continue

        print(f'Writing converted SBOL3 file to {file3}')
        doc3.write(file3, sbol3.SORTED_NTRIPLES)
        # record the conversion for later use
        mappings[file] = file3

    return mappings


def convert3to2(doc3: sbol3.Document) -> sbol2.Document:
    """Convert an SBOL3 document to an equivalent SBOL2 document

    :param doc3: Document to convert
    :return: equivalent SBOL2 document
    """
    # TODO: remove workarounds after conversion errors fixed in https://github.com/sboltools/sbolgraph/issues/16
    # remap sequence encodings:
    encoding_remapping = {
        sbol3.IUPAC_DNA_ENCODING: sbol2.SBOL_ENCODING_IUPAC,
        sbol3.IUPAC_PROTEIN_ENCODING: sbol2.SBOL_ENCODING_IUPAC_PROTEIN,
        sbol3.SMILES_ENCODING: sbol3.SMILES_ENCODING
    }
    for s in (o for o in doc3.objects if isinstance(o, sbol3.Sequence)):
        if s.encoding in encoding_remapping:
            s.encoding = encoding_remapping[s.encoding]
    # remap component types:
    type_remapping = {
        sbol3.SBO_DNA: sbol2.BIOPAX_DNA,
        sbol3.SBO_RNA: sbol2.BIOPAX_RNA,
        sbol3.SBO_PROTEIN: sbol2.BIOPAX_PROTEIN,
        sbol3.SBO_SIMPLE_CHEMICAL: sbol2.BIOPAX_SMALL_MOLECULE,
        sbol3.SBO_NON_COVALENT_COMPLEX: sbol2.BIOPAX_COMPLEX
    }
    for c in (o for o in doc3.objects if isinstance(o, sbol3.Component)):
        c.types = [(type_remapping[t] if t in type_remapping else t) for t in c.types]

    # Write to an RDF-XML temp file to run through the converter:
    sbol3_path = tempfile.mkstemp(suffix='.xml')[1]
    doc3.write(sbol3_path, sbol3.RDF_XML)

    # Run the actual conversion and return the resulting document
    cmd = [SBOL_CONVERTER, '-output', 'sbol2',
           'import', sbol3_path,
           'convert', '--target-sbol-version', '2']
    # This will raise an exception if the command fails
    proc = subprocess.run(cmd, capture_output=True, check=True)
    # Extract the rdf_xml output from the sbol converter
    rdf_xml = proc.stdout.decode('utf-8')

    doc2 = sbol2.Document()
    doc2.readString(rdf_xml)
    # TODO: remove workaround after resolution of https://github.com/SynBioDex/libSBOLj/issues/621
    for c in doc2.componentDefinitions:
        for sa in c.sequenceAnnotations:
            for loc in sa.locations:
                loc.sequence = None  # remove optional sequences, per https://github.com/SynBioDex/libSBOLj/issues/621
    doc2.validate()
    return doc2


def convert_to_fasta(doc3: sbol3.Document, path: str) -> None:
    """Convert an SBOL3 document to a FASTA file, which is written to disk
    Specifically, every Component with precisely one sequence of a nucleic acid type will result in a FASTA entry
    Components will no sequences will be silently omitted; those with multiple will result in a warning

    :param doc3: SBOL3 document to convert
    :param path: path to write FASTA file to
    """
    with open(path, 'w') as out:
        for c in id_sort([c for c in doc3.objects if isinstance(c, sbol3.Component)]):
            # Find all sequences of nucleic acid type
            na_seqs = [s.lookup() for s in c.sequences if s.lookup().encoding == sbol3.IUPAC_DNA_ENCODING]
            if len(na_seqs) == 0:  # ignore components with no sequence to serialize
                continue
            elif len(na_seqs) == 1:  # if there is precisely one sequence, write it to the FASTA
                record = SeqIO.SeqRecord(Seq(na_seqs[0].elements), id=c.display_id, description=c.description or '')
                out.write(record.format('fasta'))
            else:  # warn about components with ambiguous sequences
                logging.warning(f'Ambiguous component ({len(na_seqs)} sequences) not converted to FASTA: {c.identity}')


def convert_from_fasta(path: str, namespace: str) -> sbol3.Document:
    """Convert a FASTA nucleotide document on disk into an SBOL3 document
    Specifically, every sequence in the FASTA will be converted into an SBOL Component and associated Sequence

    :param path: path to read FASTA file from
    :param namespace: URIs of Components will be set to {namespace}/{fasta_id}
    :return: SBOL3 document containing converted materials
    """
    doc = sbol3.Document()
    with open(path, 'r') as f:
        for r in SeqIO.parse(f, 'fasta'):
            identity = namespace+'/'+string_to_display_id(r.id)
            s = sbol3.Sequence(identity+'_sequence', name=r.name, description=r.description.strip(),
                               elements=str(r.seq), encoding=sbol3.IUPAC_DNA_ENCODING, namespace=namespace)
            doc.add(s)
            doc.add(sbol3.Component(identity, sbol3.SBO_DNA, name=r.name, description=r.description.strip(),
                                    sequences=[s.identity], namespace=namespace))
    return doc


def convert_from_genbank(path: str, namespace: str) -> sbol3.Document:
    """Convert a GenBank document on disk into an SBOL3 document
    Specifically, the GenBank document is first imported to SBOL2, then converted from SBOL2 to SBOL3

    :param path: path to read GenBank file from
    :param namespace: URIs of Components will be set to {namespace}/{genbank_id}
    :return: SBOL3 document containing converted materials
    """
    doc2 = sbol2.Document()
    sbol2.setHomespace(namespace)
    doc2.importFromFormat(path)
    doc = convert2to3(doc2, [namespace])
    return doc


def convert_to_genbank(doc3: sbol3.Document, path: str) -> list[SeqRecord]:
    """Convert an SBOL3 document to a GenBank file, which is written to disk
    Note that for compatibility with version control software, if no prov:modified term is available on each Component,
    then a fixed bogus datestamp of January 1, 2000 is given

    :param doc3: SBOL3 document to convert
    :param path: path to write FASTA file to
    """
    # first convert to SBOL2, then export to a temp GenBank file
    doc2 = convert3to2(doc3)

    # TODO: remove this kludge after resolution of https://github.com/SynBioDex/libSBOLj/issues/622
    keepers = {'http://sbols.org/v2', 'http://www.w3.org/ns/prov', 'http://purl.org/dc/terms/',
               'http://sboltools.org/backport'}
    for c in doc2.componentDefinitions: # wipe out all annotation properties
        c.properties = {p:v for p,v in c.properties.items() if any(k for k in keepers if p.startswith(k))}

    gb_tmp = tempfile.mkstemp(suffix='.gb')[1]
    if not doc2.componentDefinitions: # if there's no content, doc2.exportToFormat errors, so write an empty file
        open(gb_tmp, 'w').close() # TODO: remove after resolution of https://github.com/SynBioDex/pySBOL2/issues/401
    else:
        doc2.exportToFormat('GenBank', gb_tmp)

    # Read and re-write in order to sort and to purge invalid date information and standardize GenBank formatting
    with open(gb_tmp, 'r') as tmp:
        records = {r.id: r for r in SeqIO.parse(tmp, 'gb')}
    sorted_records = [records[r_id] for r_id in sorted(records)]
    # also sort the order of the feature qualifiers to ensure they remain stable
    for r in sorted_records:
        for f in r.features:
            f.qualifiers = {k: f.qualifiers[k] for k in sorted(f.qualifiers)}

    # write the final file
    SeqIO.write(sorted_records, path, 'gb')
    return sorted_records
