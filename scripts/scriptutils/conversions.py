import datetime
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
    for s, p, o in g.triples((None,rdflib.RDF.type,None)):
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


def convert2to3(sbol2_doc: Union[str, sbol2.Document], namespaces: list[str] = []) -> sbol3.Document:
    """Convert an SBOL2 document to an equivalent SBOL3 document

    :param sbol2_doc: Document to convert
    :param namespaces: list of URI prefixes to treat as namespaces
    :return: equivalent SBOL3 document
    """
    # if we've started with a Document in memory, write it to a temp file
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
        server = urllib.parse.urlunparse([p.scheme,p.netloc,'','','',''])
        o.namespace = server
    # infer sequences for locations:
    for s in (o for o in doc.objects if isinstance(o,sbol3.Component)):
        if len(s.sequences) != 1: # can only infer sequences if there is precisely one
            continue
        for f in (f for f in s.features if isinstance(f,sbol3.SequenceFeature) or isinstance(f,sbol3.SubComponent)):
            for l in f.locations:
                l.sequence = s.sequences[0]
    # remap sequence encodings:
    encoding_remapping = {
        'http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html': 'https://identifiers.org/edam:format_1207',
        'http://www.chem.qmul.ac.uk/iupac/AminoAcid/': 'https://identifiers.org/edam:format_1208',
        'http://www.opensmiles.org/opensmiles.html': 'https://identifiers.org/edam:format_1196'
    }
    for s in (o for o in doc.objects if isinstance(o,sbol3.Sequence)):
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
    # TODO: remove workarounds after conversion errors fixed in https://github.com/sboltools/sbolgraph/issues/14
    # remap sequence encodings:
    encoding_remapping = {
        sbol3.IUPAC_DNA_ENCODING: sbol2.SBOL_ENCODING_IUPAC,
        sbol3.IUPAC_PROTEIN_ENCODING: sbol2.SBOL_ENCODING_IUPAC_PROTEIN,
        sbol3.SMILES_ENCODING: sbol3.SMILES_ENCODING
    }
    for s in (o for o in doc3.objects if isinstance(o,sbol3.Sequence)):
        if s.encoding in encoding_remapping:
            s.encoding = encoding_remapping[s.encoding]

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
                record = SeqIO.SeqRecord(na_seqs[0].elements.upper(), id=c.display_id)
                out.write(record.format('fasta'))
            else:  # warn about components with ambiguous sequences
                logging.warning(f'Ambiguous component ({len(na_seqs)} sequences) not converted to FASTA: {c.identity}')


DEFAULT_BOGUS_GENBANK_DATE = '01-JAN-2000'
PROV_MODIFIED = 'http://purl.org/dc/terms/modified'
def convert_to_genbank(doc3: sbol3.Document, path: str) -> list[SeqRecord]:
    """Convert an SBOL3 document to a GenBank file, which is written to disk
    Note that for compatibility with version control software, if no prov:modified term is available on each Component,
    then a fixed bogus datestamp of January 1, 2000 is given

    :param doc3: SBOL3 document to convert
    :param path: path to write FASTA file to
    """
    # first convert to SBOL2, then export to a temp GenBank file
    doc2 = convert3to2(doc3)
    gb_tmp = tempfile.mkstemp(suffix='.gb')[1]
    doc2.exportToFormat('GenBank', gb_tmp)

    # Read and re-write in order to  purge invalid date information and standardize GenBank formatting
    # next, build the map of modification datestamps
    mod_dates = {}
    for c in id_sort([c for c in doc3.objects if isinstance(c, sbol3.Component)]):
        # since GenBank exports have only display_id values, if there's a collision we can't map modified dates
        if c.display_id in mod_dates:
            logging.warning(f'Multiple uses of display_id, so GenBank modified date cannot be assigned: {c.identity}')
            mod_dates[c.display_id] = DEFAULT_BOGUS_GENBANK_DATE
        # if there is a modified property, convert it to the required format
        if PROV_MODIFIED in c.properties and len(c._properties[PROV_MODIFIED]):  # TODO: figure out how to do this without accessing a protected member
            try:
                mod = str(sorted(c._properties[PROV_MODIFIED])[-1])  # sort & take last time
                mod_dates[c.display_id] = datetime.datetime.strptime(mod.split('T')[0], '%Y-%m-%d').strftime("%Y-%b-%d")
            except ValueError:
                mod_dates[c.display_id] = DEFAULT_BOGUS_GENBANK_DATE
        else:
            mod_dates[c.display_id] = DEFAULT_BOGUS_GENBANK_DATE

    # read the GenBank file back in and remap using corresponding modification datestamps
    with open(gb_tmp, 'r') as tmp:
        records = [r for r in SeqIO.parse(tmp, 'gb')]
        # for r in records:
        #     r.annotations['date'] = mod_dates[r.name]  # Should always be there; if not, converter has failed
    # write the final file
    SeqIO.write(records,path,'gb')
    return records
