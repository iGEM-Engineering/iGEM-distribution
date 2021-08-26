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
        unique_parts = set(inventory.values())
        print(f'Unique parts found: {unique_parts}')
        assert len(unique_parts) == 4, f'Expected 4 parts, but found {len(unique_parts)}: {unique_parts}'
        assert len(inventory) == 6, f'Expected 6 keys, but found {len(inventory)}: {inventory}'
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}NM_005341_4': f'{pkg}NM_005341_4',
                    f'{pkg}NM_005342': f'{pkg}NM_005342_4',
                    f'{pkg}NM_005342_4': f'{pkg}NM_005342_4',
                    f'{pkg}NM_005343': f'{pkg}NM_005343_4',
                    f'{pkg}NM_005343_4': f'{pkg}NM_005343_4',
                    'http://parts.igem.org/J23101':'http://parts.igem.org/J23101'}
        assert inventory == expected, f'Inventory does not match expected value: {inventory}'

    def test_import(self):
        """Test ability to retrieve parts from GenBank and iGEM"""
        tmpsub = copy_to_tmp()

        # first round of import should obtain all but one missing part
        retrieved = scripts.scriptutils.part_retrieval.import_parts(tmpsub)
        assert len(retrieved) == 4
        expected = ['https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1', 'http://parts.igem.org/J23100',
                    'http://parts.igem.org/J23102', 'http://parts.igem.org/pSB1C3']
        assert retrieved == expected, f'Retrieved parts list does not match expected value: {retrieved}'
        testdir = os.path.dirname(os.path.realpath(__file__))
        # note: targets to check doesn't include SBOL2 cache, since that isn't serialized in predictable order
        targets = [scripts.scriptutils.IGEM_FASTA_CACHE_FILE, scripts.scriptutils.GENBANK_CACHE_FILE]
        for t in targets:
            test_file = os.path.join(tmpsub, t)
            comparison_file = os.path.join(testdir, 'testfiles', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

        # running import again should download nothing new but continue with just the one part
        retrieved = scripts.scriptutils.part_retrieval.import_parts(tmpsub)
        assert len(retrieved) == 0
        for t in targets:
            test_file = os.path.join(tmpsub, t)
            comparison_file = os.path.join(testdir, 'testfiles', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'


if __name__ == '__main__':
    unittest.main()
