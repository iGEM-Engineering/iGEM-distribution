import unittest
import tempfile
import os
from shutil import copy
import scripts.scriptutils


class TestDirectoryRegularization(unittest.TestCase):
    def test_directory_regularization(self):
        # copy file into temp directory and make the export subdirectory
        tmpdir = tempfile.mkdtemp()
        # validation should fail due to lack of Excel file
        try:
            scripts.scriptutils.regularize_directory(tmpdir)
            raise AssertionError('Validation should fail when Excel file is missing')
        except ValueError as e:
            assert str(e) == f' Could not find package excel file'

        # copy over package file, which should allow validation to succeed
        testdir = os.path.dirname(os.path.realpath(__file__))
        copy(os.path.join(os.path.dirname(os.path.dirname(testdir)), 'package template.xlsx'), tmpdir)

        scripts.scriptutils.regularize_directory(tmpdir)
        assert os.path.isdir(os.path.join(tmpdir, scripts.scriptutils.EXPORT_DIRECTORY))

        # copy template again, which should cause a failure for multiple excel files
        copy(os.path.join(os.path.dirname(os.path.dirname(testdir)), 'package template.xlsx'),
             os.path.join(tmpdir, 'package template2.xlsx'))
        try:
            scripts.scriptutils.regularize_directory(tmpdir)
            raise AssertionError('Validation should fail with multiple Excel files')
        except ValueError as e:
            assert str(e).startswith(' Found multiple Excel files in package')

        # make another subdirectory, which should cause a failure for multiple subdirectories
        tmpsub = os.path.join(tmpdir, 'extra_directory')
        os.mkdir(tmpsub)
        try:
            scripts.scriptutils.regularize_directory(tmpdir)
            raise AssertionError('Validation should fail with multiple subdirectories')
        except ValueError as e:
            assert str(e) == f' Found unexpected subdirectories: extra_directory'


if __name__ == '__main__':
    unittest.main()
