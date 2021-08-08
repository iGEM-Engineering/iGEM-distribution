import unittest
import tempfile
import os
import filecmp
from shutil import copy
from scripts.scriptutils import part_retrieval
import scripts.scriptutils


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
    copy(os.path.join(testdir, 'testfiles', scripts.scriptutils.EXPORT_DIRECTORY, 'package_specification.nt'), tmpexport)
    return tmpsub


class TestImportParts(unittest.TestCase):
    def test_inventory(self):
        """Test ability to take inventory of parts already in a directory"""
        tmpsub = copy_to_tmp()
        inventory = part_retrieval.package_parts_inventory(tmpsub)
        print(f'Found parts: {inventory}')
        assert len(inventory) == 4, f'Expected 4 parts, but found {len(inventory)}: {inventory}'
        expected = ['https://github.com/iGEM-Engineering/iGEM-distribution/test_package/NM_005341_4',
                    'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/NM_005342_4',
                    'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/NM_005343_4',
                    'https://synbiohub.org/public/igem/BBa_J23101']
        assert inventory == expected, f'Inventory does not match expected value: {inventory}'

    def test_import(self):
        # first round of import should obtain all but one missing part
        #assert filecmp.cmp(test_file, comparison_file), "Downloaded GenBank is not identical"

        # running import again should download nothing new but continue with just the one part
        #assert filecmp.cmp(test_file, comparison_file), "Downloaded GenBank is not identical"
        pass


if __name__ == '__main__':
    unittest.main()
