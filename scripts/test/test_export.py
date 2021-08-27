import unittest
import tempfile
import os
import filecmp
from shutil import copy
import scripts.scriptutils

class TestExportCSV(unittest.TestCase):
    def test_csv_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(tmpdir, scripts.scriptutils.EXPORT_DIRECTORY))
        testdir = os.path.dirname(os.path.realpath(__file__))
        copy(os.path.join(os.path.dirname(os.path.dirname(testdir)), 'package template.xlsx'), tmpdir)

        # run the export script
        scripts.scriptutils.export_csvs(tmpdir)

        # check if the values are as expected
        test_file = os.path.join(tmpdir, scripts.scriptutils.EXPORT_DIRECTORY, 'Libraries and Composites.csv')
        comparison_file = os.path.join(testdir, 'testfiles', 'Libraries and Composites.csv')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "Library and Composites exports are not identical"

        test_file = os.path.join(tmpdir, scripts.scriptutils.EXPORT_DIRECTORY, 'Parts and Devices.csv')
        comparison_file = os.path.join(testdir, 'testfiles', 'Parts and Devices.csv')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "Library and Composites exports are not identical"

    def test_sbol_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpdir = tempfile.mkdtemp()
        tmpsub = os.path.join(tmpdir,'test_package')
        os.mkdir(tmpsub)
        os.mkdir(os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY))
        testdir = os.path.dirname(os.path.realpath(__file__))
        copy(os.path.join(os.path.dirname(os.path.dirname(testdir)), 'package template.xlsx'), tmpsub)

        # run the export script
        scripts.scriptutils.export_sbol(tmpsub)

        # check if the values are as expected
        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, scripts.scriptutils.SBOL_EXPORT_NAME)
        comparison_file = os.path.join(testdir, 'testfiles', 'package_specification.nt')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "SBOL exports are not identical"

    def test_complex_sbol_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpdir = tempfile.mkdtemp()
        tmpsub = os.path.join(tmpdir,'test_package')
        os.mkdir(tmpsub)
        os.mkdir(os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY))
        testdir = os.path.dirname(os.path.realpath(__file__))
        copy(os.path.join('testfiles', 'test_package.xlsx'), tmpsub)

        # run the export script
        scripts.scriptutils.export_sbol(tmpsub)

        # check if the values are as expected
        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, scripts.scriptutils.SBOL_EXPORT_NAME)
        comparison_file = os.path.join(testdir, 'testfiles', 'views', 'package_specification.nt')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "SBOL exports are not identical"


if __name__ == '__main__':
    unittest.main()
