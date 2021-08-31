import unittest
import os
import filecmp
import scripts.scriptutils

from scripts.test.helpers import copy_to_tmp

template_path = os.path.join(os.path.pardir, os.path.pardir, os.path.pardir, 'package template.xlsx')


class TestExportCSV(unittest.TestCase):
    def test_csv_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpsub = copy_to_tmp(package=[template_path])
        testdir = os.path.dirname(os.path.realpath(__file__))

        # run the export script
        scripts.scriptutils.export_csvs(tmpsub)

        # check if the values are as expected
        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, 'Libraries and Composites.csv')
        comparison_file = os.path.join(testdir, 'test_files', 'Libraries and Composites.csv')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "Library and Composites exports are not identical"

        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, 'Parts and Devices.csv')
        comparison_file = os.path.join(testdir, 'test_files', 'Parts and Devices.csv')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "Library and Composites exports are not identical"

    def test_sbol_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpsub = copy_to_tmp(package=[template_path])
        testdir = os.path.dirname(os.path.realpath(__file__))

        # run the export script
        scripts.scriptutils.export_sbol(tmpsub)

        # check if the values are as expected
        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, scripts.scriptutils.SBOL_EXPORT_NAME)
        comparison_file = os.path.join(testdir, 'test_files', 'package_specification.nt')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "SBOL exports are not identical"

    def test_complex_sbol_export(self):
        # copy file into temp directory and make the export subdirectory
        tmpsub = copy_to_tmp(package=['test_package.xlsx'])
        testdir = os.path.dirname(os.path.realpath(__file__))

        # run the export script
        scripts.scriptutils.export_sbol(tmpsub)

        # check if the values are as expected
        test_file = os.path.join(tmpsub, scripts.scriptutils.EXPORT_DIRECTORY, scripts.scriptutils.SBOL_EXPORT_NAME)
        comparison_file = os.path.join(testdir, 'test_files', 'views', 'package_specification.nt')
        print(f'Comparing {test_file} and {comparison_file}')
        assert filecmp.cmp(test_file, comparison_file), "SBOL exports are not identical"


if __name__ == '__main__':
    unittest.main()
