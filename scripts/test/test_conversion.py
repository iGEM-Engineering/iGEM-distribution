import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol2
import sbol3

import scripts.scriptutils


import difflib
import sys

def copy_to_tmp() -> str:
    """Copy common test files into a temporary package directory

    :return: temporary package directory
    """
    # make a temporary package directory and export directory
    tmpdir = tempfile.mkdtemp()
    tmpsub = os.path.join(tmpdir, 'test_package')
    tmpexport = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY)
    os.mkdir(tmpsub)
    os.mkdir(tmpexport)
    # copy all of the relevant files
    testdir = os.path.dirname(os.path.realpath(__file__))
    print(f'test file is {__file__}')
    copy(os.path.join(testdir, 'testfiles', 'test_sequence.fasta'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'two_sequences.gb'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'BBa_J23101.xml'), tmpsub)
    return tmpsub


class Test2To3Conversion(unittest.TestCase):
    def test_convert_identities(self):
        """Test conversion of a complex file"""
        testdir = os.path.dirname(os.path.realpath(__file__))
        input_path = os.path.join(testdir, 'testfiles', 'sbol3-small-molecule.rdf')
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
        input_path = os.path.join(testdir, 'testfiles', 'sbol3-small-molecule.rdf')
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
        tmpsub = copy_to_tmp()
        mappings = scripts.scriptutils.convert_package_sbol2_files(tmpsub)
        expected = {os.path.join(tmpsub, 'BBa_J23101.xml'): os.path.join(tmpsub, 'BBa_J23101.nt')}
        assert mappings == expected, f'Conversion mappings do not match expected value: {mappings}'

        testdir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(testdir, 'testfiles', 'BBa_J23101.nt')

        assert filecmp.cmp(os.path.join(tmpsub, 'BBa_J23101.nt'), comparison_file), \
            f'Converted file {comparison_file} is not identical'

if __name__ == '__main__':
    unittest.main()
