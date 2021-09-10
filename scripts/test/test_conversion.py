import unittest
import os
import filecmp

import sbol2
import sbol3
from Bio import SeqIO
import datetime

import scripts.scriptutils
from scripts.test.helpers import copy_to_tmp


class Test2To3Conversion(unittest.TestCase):
    def test_convert_identities(self):
        """Test conversion of a complex file"""
        testdir = os.path.dirname(os.path.realpath(__file__))
        input_path = os.path.join(testdir, 'test_files', 'sbol3-small-molecule.rdf')
        doc = scripts.scriptutils.convert2to3(input_path)
        # check for issues in converted document
        report = doc.validate()
        for issue in report:
            print(issue)
        assert len(report) == 0
        # Expecting 9 top level objects, 4 Components, 4 Sequences, and 1 prov:Activity
        self.assertEqual(9, len(doc.objects))

    def test_convert_object(self):
        """Test conversion of a loaded SBOL2 document"""
        testdir = os.path.dirname(os.path.realpath(__file__))
        input_path = os.path.join(testdir, 'test_files', 'sbol3-small-molecule.rdf')
        doc2 = sbol2.Document()
        doc2.read(input_path)
        doc = scripts.scriptutils.convert2to3(doc2)
        # check for issues in converted document
        report = doc.validate()
        for issue in report:
            print(issue)
        assert len(report) == 0
        # Expecting 9 top level objects, 4 Components, 4 Sequences, and 1 prov:Activity
        self.assertEqual(9, len(doc.objects))

    def test_2to3_conversion(self):
        """Test ability to convert parts already in a directory"""
        tmpsub = copy_to_tmp(package = ['test_sequence.fasta', 'two_sequences.gb', 'BBa_J23101.xml'])
        mappings = scripts.scriptutils.convert_package_sbol2_files(tmpsub)
        expected = {os.path.join(tmpsub, 'BBa_J23101.xml'): os.path.join(tmpsub, 'BBa_J23101.nt')}
        assert mappings == expected, f'Conversion mappings do not match expected value: {mappings}'

        testdir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(testdir, 'test_files', 'BBa_J23101.nt')

        assert filecmp.cmp(os.path.join(tmpsub, 'BBa_J23101.nt'), comparison_file), \
            f'Converted file {comparison_file} is not identical'

    def test_3to2_conversion(self):
        """Test ability to convert from SBOL3 to SBOL2"""
        # Get the SBOL3 test document
        tmpsub = copy_to_tmp(package = ['BBa_J23101.nt'])
        doc3 = sbol3.Document()
        doc3.read(os.path.join(tmpsub, 'BBa_J23101.nt'))

        # Convert to SBOL2 and check contents
        doc2 = scripts.scriptutils.convert3to2(doc3)
        assert len(doc2.componentDefinitions) == 1, f'Expected 1 CD, but found {len(doc2.componentDefinitions)}'
        # TODO: bring this back after resolution of https://github.com/sboltools/sbolgraph/issues/15
        #assert len(doc2.activities) == 1, f'Expected 1 Activity, but found {len(doc2.activities)}'
        assert len(doc2.sequences) == 1, f'Expected 1 Sequence, but found {len(doc2.sequences)}'
        assert doc2.componentDefinitions[0].identity == 'https://synbiohub.org/public/igem/BBa_J23101'
        assert doc2.componentDefinitions[0].sequences[0] == 'https://synbiohub.org/public/igem/BBa_J23101_sequence'
        assert doc2.sequences[0].encoding == 'http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html'
        assert doc2.sequences[0].elements == 'tttacagctagctcagtcctaggtattatgctagc'

    def test_genbank_conversion(self):
        """Test ability to convert from SBOL3 to GenBank"""
        # Get the SBOL3 test document
        tmpsub = copy_to_tmp(package=['BBa_J23101.nt'])
        doc3 = sbol3.Document()
        doc3.read(os.path.join(tmpsub, 'BBa_J23101.nt'))

        # Convert to GenBank and check contents
        outfile = os.path.join(tmpsub, 'BBa_J23101.gb')
        scripts.scriptutils.convert_to_genbank(doc3, outfile)

        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'BBa_J23101.gb')
        assert filecmp.cmp(outfile, comparison_file), f'Converted GenBank file {comparison_file} is not identical'

    def test_genbank_multi_conversion(self):
        """Test ability to convert from SBOL3 to GenBank"""
        # Get the SBOL3 test document
        tmpsub = copy_to_tmp(package=['iGEM_SBOL2_imports.nt'])
        doc3 = sbol3.Document()
        doc3.read(os.path.join(tmpsub, 'iGEM_SBOL2_imports.nt'))

        # Convert to GenBank and check contents
        outfile = os.path.join(tmpsub, 'iGEM_SBOL2_imports.gb')
        scripts.scriptutils.convert_to_genbank(doc3, outfile)

        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'iGEM_SBOL2_imports.gb')
        assert filecmp.cmp(outfile, comparison_file), f'Converted GenBank file {comparison_file} is not identical'

    def test_fasta_conversion(self):
        """Test ability to convert from SBOL3 to FASTA"""
        # Get the SBOL3 test document
        tmpsub = copy_to_tmp(package=['BBa_J23101.nt'])
        doc3 = sbol3.Document()
        doc3.read(os.path.join(tmpsub, 'BBa_J23101.nt'))

        # Convert to SBOL2 and check contents
        outfile = os.path.join(tmpsub, 'BBa_J23101.fasta')
        scripts.scriptutils.convert_to_fasta(doc3, outfile)

        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'BBa_J23101.fasta')
        assert filecmp.cmp(outfile, comparison_file), f'Converted FASTA file {comparison_file} is not identical'

if __name__ == '__main__':
    unittest.main()
