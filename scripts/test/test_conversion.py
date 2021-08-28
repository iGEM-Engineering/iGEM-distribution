import unittest
import tempfile
import os
import filecmp
from shutil import copy

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
        testdir = os.path.dirname(os.path.realpath(__file__))
        input_path = os.path.join(testdir, 'testfiles', 'sbol3-small-molecule.rdf')
        with open(input_path) as fp:
            rdf_data = fp.read()
        rdf_data = scripts.scriptutils.convert_identities2to3(rdf_data)
        self.assertIsNotNone(rdf_data)
        doc = sbol3.Document()
        doc.read_string(rdf_data, sbol3.RDF_XML)
        # Expecting 8 top level objects, 4 Components and 4 Sequences
        self.assertEqual(8, len(doc.objects))

    def test_2to3_conversion(self):
        """Test ability to take inventory of parts already in a directory"""
        tmpsub = copy_to_tmp()
        mappings = scripts.scriptutils.convert_package_sbol2_files(tmpsub)
        expected = {os.path.join(tmpsub, 'BBa_J23101.xml'): os.path.join(tmpsub, 'BBa_J23101.nt')}
        assert mappings == expected, f'Conversion mappings do not match expected value: {mappings}'

        testdir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(testdir, 'testfiles', 'BBa_J23101.nt')

        print('Showing differences:')
        with open(os.path.join(tmpsub, 'BBa_J23101.nt'), 'r') as f1:
            with open(comparison_file, 'r') as f2:
                diff = difflib.unified_diff(
                    f1.readlines(),
                    f2.readlines(),
                    fromfile='generated',
                    tofile='expected',
                )
                for line in diff:
                    sys.stdout.write(line)
        print('End of differences')

        assert filecmp.cmp(os.path.join(tmpsub, 'BBa_J23101.nt'), comparison_file), \
            f'Converted file {comparison_file} is not identical'


if __name__ == '__main__':
    unittest.main()
