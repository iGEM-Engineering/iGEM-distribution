import unittest
import os
import filecmp

import scripts.scriptutils
from scripts.test.helpers import copy_to_tmp


class Test2To3Conversion(unittest.TestCase):
    def test_2to3_package_conversion(self):
        """Test ability to convert parts already in a directory"""
        tmpsub = copy_to_tmp(package=['test_sequence.fasta', 'two_sequences.gb', 'BBa_J23101.xml'])
        mappings = scripts.scriptutils.convert_package_sbol2_files(tmpsub)
        expected = {os.path.join(tmpsub, 'BBa_J23101.xml'): os.path.join(tmpsub, 'BBa_J23101.nt')}
        assert mappings == expected, f'Conversion mappings do not match expected value: {mappings}'

        testdir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(testdir, 'test_files', 'BBa_J23101.nt')
        assert filecmp.cmp(os.path.join(tmpsub, 'BBa_J23101.nt'), comparison_file), \
            f'Converted file {comparison_file} is not identical'

    def test_2to3_package_merge(self):
        """Test ability to convert parts already in a directory"""
        tmpsub = copy_to_tmp(package=['test_sequence.fasta', 'two_sequences.gb', 'BBa_J23101.xml'],
                             renames={'BBa_J23101_and_J23102.nt': 'BBa_J23101.nt'})
        mappings = scripts.scriptutils.convert_package_sbol2_files(tmpsub)
        expected = {os.path.join(tmpsub, 'BBa_J23101.xml'): os.path.join(tmpsub, 'BBa_J23101.nt')}
        assert mappings == expected, f'Conversion mappings do not match expected value: {mappings}'

        testdir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(testdir, 'test_files', 'BBa_J23101_and_J23102.nt')
        assert filecmp.cmp(os.path.join(tmpsub, 'BBa_J23101.nt'), comparison_file), \
            f'Converted file {comparison_file} is not identical'


if __name__ == '__main__':
    unittest.main()
