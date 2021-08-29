import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

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
    copy(os.path.join(testdir, 'testfiles', 'J23102-modified.fasta'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'two_sequences.gb'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'BBa_J23101.xml'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', scripts.scriptutils.EXPORT_DIRECTORY, 'package_specification.nt'), tmpexport)
    return tmpsub


class TestImportParts(unittest.TestCase):
    def test_inventory(self):
        """Test ability to take inventory of parts already in a directory"""
        tmpsub = copy_to_tmp()
        inventory = part_retrieval.package_parts_inventory(tmpsub)
        unique_parts = set(inventory.locations.keys())
        assert len(unique_parts) == 5, f'Expected 5 parts, found {len(unique_parts)}: {unique_parts}'
        assert len(inventory.aliases) == 8, f'Expected 8 aliases, found {len(inventory.aliases)}: {inventory.aliases}'
        assert len(inventory.files) == 4, \
            f'Expected 4 files, found {len(inventory.files)}: {[f.path for f in inventory.files]}'
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}NM_005341_4': f'{pkg}NM_005341_4',
                    f'{pkg}NM_005342': f'{pkg}NM_005342_4',
                    f'{pkg}NM_005342_4': f'{pkg}NM_005342_4',
                    f'{pkg}NM_005343': f'{pkg}NM_005343_4',
                    f'{pkg}NM_005343_4': f'{pkg}NM_005343_4',
                    'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/J23102-modified':
                        'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/J23102-modified',
                    'http://parts.igem.org/J23101':'http://parts.igem.org/J23101',
                    'http://parts.igem.org/J23101/1': 'http://parts.igem.org/J23101'}
        assert inventory.aliases == expected, f'Inventory aliases do not match expected value: {inventory.aliases}'

    def test_import(self):
        """Test ability to retrieve parts from GenBank and iGEM"""
        tmpsub = copy_to_tmp()

        # first round of import should obtain all but one missing part
        retrieved = scripts.scriptutils.part_retrieval.import_parts(tmpsub)
        assert len(retrieved) == 5
        expected = ['https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1', 'http://parts.igem.org/J23100',
                    'http://parts.igem.org/J23102', 'http://parts.igem.org/pSB1C3',
                    'https://synbiohub.programmingbiology.org/public/Eco1C1G1T1/LmrA']
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

    def test_collation(self):
        """Test ability to collate parts based on a specification"""
        tmpsub = copy_to_tmp()
        doc = part_retrieval.collate_package(tmpsub)
        # composite document should have 5 imported parts plus 6 parts that aren't yet imported, plus 2 templates
        # currently has an extra due
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}Anderson_Promoters_in_vector_ins_template', f'{pkg}Anderson_Promoters_in_vector_template',
                    'http://parts.igem.org/J23100', 'http://parts.igem.org/J23101', 'http://parts.igem.org/J23102',
                    'http://parts.igem.org/pSB1C3', f'{pkg}pOpen_v4',
                    'https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1',
                    'https://synbiohub.programmingbiology.org/public/Eco1C1G1T1/LmrA',
                    f'{pkg}J23102_modified',
                    # TODO: import issues to fix:
                    f'{pkg}NM_005341_4', f'{pkg}NM_005342', f'{pkg}NM_005343', # TODO: should these be bare or versioned?
                    'https://synbiohub.org/public/igem/BBa_J23101' # TODO: duplicate of 'http://parts.igem.org/J23101': which ID should it be?
                    }
        collated = {o.identity for o in doc.objects if isinstance(o, sbol3.Component)}
        assert collated == expected, f'Collated parts set does not match expected value: {collated}'
        sequences = [o for o in doc.objects if isinstance(o,sbol3.Sequence)]
        assert len(sequences) == 5, f'Collated document should have 5 sequences, but has only {len(sequences)}'
        # Total: 14 components, 5 sequences, 4 collections, 2 CDs, 1 Activity = 26
        assert len(doc.objects) == 26, f'Expected 26 TopLevel objects, but found {len(doc.objects)}'


if __name__ == '__main__':
    unittest.main()
