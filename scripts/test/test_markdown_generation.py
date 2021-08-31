import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

from scripts.scriptutils import EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, SUMMARY_FILE, generate_package_summary
from scripts.test.helpers import copy_to_tmp


class TestMarkdownGeneration(unittest.TestCase):
    def test_readme_generation(self):
        """Test ability to generate a markdown readme"""
        tmp_sub = copy_to_tmp()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        input_doc = os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, 'package-expanded.nt')

        # Read and convert document
        doc = sbol3.Document()
        doc.read(input_doc)
        generate_package_summary(tmp_sub, doc)

        # Check if it's the same
        generated_file = os.path.join(tmp_sub, SUMMARY_FILE)
        comparison_file = os.path.join(test_dir, 'test_files', SUMMARY_FILE)
        assert filecmp.cmp(generated_file, comparison_file), \
            f'Generated file {generated_file} is not identical'

if __name__ == '__main__':
    unittest.main()
