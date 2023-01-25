import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

from scripts.scriptutils import EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, SUMMARY_FILE, generate_package_summary, \
    DISTRIBUTION_NAME, DISTRIBUTION_SUMMARY, generate_distribution_summary
from scripts.test.helpers import copy_to_tmp


class TestMarkdownGeneration(unittest.TestCase):
    def test_readme_generation(self):
        """Test ability to generate a markdown readme"""
        rm = {os.path.join(EXPORT_DIRECTORY, 'package-expanded.nt'): os.path.join(EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)}
        tmp_sub = copy_to_tmp(renames=rm)

        # Read and convert document
        doc = sbol3.Document()
        doc.read(os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))
        generate_package_summary(tmp_sub, doc)

        # Check if it's the same
        generated_file = os.path.join(tmp_sub, SUMMARY_FILE)
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', SUMMARY_FILE)
        assert filecmp.cmp(generated_file, comparison_file), f'Generated file {generated_file} is not identical'

    def test_distribution_readme_generation(self):
        """Test ability to generate whole-distribution markdown readme"""
        rm = {os.path.join('distribution', DISTRIBUTION_NAME): os.path.join(DISTRIBUTION_NAME)}
        tmp_sub = copy_to_tmp(renames=rm)

        # Read and convert document
        doc = sbol3.Document()
        doc.read(os.path.join(tmp_sub, DISTRIBUTION_NAME))
        generate_distribution_summary(tmp_sub, doc)

        # Check if it's the same
        generated_file = os.path.join(tmp_sub, DISTRIBUTION_SUMMARY)
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'distribution', DISTRIBUTION_SUMMARY)
        assert filecmp.cmp(generated_file, comparison_file), f'Generated file {generated_file} is not identical'


if __name__ == '__main__':
    unittest.main()
