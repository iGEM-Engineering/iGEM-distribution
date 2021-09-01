import unittest
import os
import filecmp

import sbol2

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

if __name__ == '__main__':
    unittest.main()
