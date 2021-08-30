import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

from scripts.scriptutils import EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, SUMMARY_FILE, generate_package_summary

import difflib
import sys

def copy_to_tmp() -> str:
    """Copy common test files into a temporary package directory

    :return: temporary package directory
    """
    # make a temporary package directory and export directory
    tmpdir = tempfile.mkdtemp()
    tmpsub = os.path.join(tmpdir, 'test_package')
    tmpexport = os.path.join(tmpsub, EXPORT_DIRECTORY)
    os.mkdir(tmpsub)
    os.mkdir(tmpexport)
    # copy all of the relevant files
    testdir = os.path.dirname(os.path.realpath(__file__))
    print(f'test file is {__file__}')
    copy(os.path.join(testdir, 'testfiles', EXPORT_DIRECTORY, SBOL_PACKAGE_NAME), tmpexport)
    copy(os.path.join(testdir, 'testfiles', SUMMARY_FILE), tmpsub)
    return tmpsub


class TestMarkdownGeneration(unittest.TestCase):
    def test_readme_generation(self):
        """Test ability to generate a markdown readme"""
        tmpsub = copy_to_tmp()
        doc = sbol3.Document()
        doc.read(os.path.join(tmpsub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))
        generate_package_summary(tmpsub, doc)

        testdir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(tmpsub, SUMMARY_FILE)
        comparison_file = os.path.join(testdir, 'testfiles', SUMMARY_FILE)

        assert filecmp.cmp(test_file, comparison_file), \
            f'Generated file {test_file} is not identical'

if __name__ == '__main__':
    unittest.main()
