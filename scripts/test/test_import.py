import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

from scripts.scriptutils import part_retrieval, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, IGEM_FASTA_CACHE_FILE, \
    GENBANK_CACHE_FILE, convert_package_sbol2_files


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
    copy(os.path.join(testdir, 'testfiles', 'test_sequence.fasta'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'J23102-modified.fasta'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'two_sequences.gb'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', 'BBa_J23101.nt'), tmpsub)
    copy(os.path.join(testdir, 'testfiles', EXPORT_DIRECTORY, 'package_specification.nt'), tmpexport)
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
                    f'{pkg}NM_005342': f'{pkg}NM_005342',
                    f'{pkg}NM_005342_4': f'{pkg}NM_005342',
                    f'{pkg}NM_005343': f'{pkg}NM_005343',
                    f'{pkg}NM_005343_4': f'{pkg}NM_005343',
                    'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/J23102_modified':
                        'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/J23102_modified',
                    'https://synbiohub.org/public/igem/BBa_J23101': 'https://synbiohub.org/public/igem/BBa_J23101',
                    'http://parts.igem.org/J23101': 'https://synbiohub.org/public/igem/BBa_J23101'}
        assert inventory.aliases == expected, f'Inventory aliases do not match expected value: {inventory.aliases}'

    def test_import(self):
        """Test ability to retrieve parts from GenBank and iGEM"""
        tmpsub = copy_to_tmp()

        # first round of import should obtain all but one missing part
        retrieved = part_retrieval.import_parts(tmpsub)
        assert len(retrieved) == 5
        expected = ['https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1', 'http://parts.igem.org/J23100',
                    'http://parts.igem.org/J23102', 'http://parts.igem.org/pSB1C3',
                    'https://synbiohub.programmingbiology.org/public/Eco1C1G1T1/LmrA']
        assert retrieved == expected, f'Retrieved parts list does not match expected value: {retrieved}'
        testdir = os.path.dirname(os.path.realpath(__file__))
        # convert the retrieved SBOL2 file to SBOL3
        convert_package_sbol2_files(tmpsub)
        targets = [IGEM_FASTA_CACHE_FILE, GENBANK_CACHE_FILE, 'iGEM_SBOL2_imports.nt']
        for t in targets:
            test_file = os.path.join(tmpsub, t)
            comparison_file = os.path.join(testdir, 'testfiles', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'


        # running import again should download nothing new but continue with just the one part
        retrieved = part_retrieval.import_parts(tmpsub)
        assert len(retrieved) == 0
        for t in targets:
            test_file = os.path.join(tmpsub, t)
            comparison_file = os.path.join(testdir, 'testfiles', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

    def test_collation(self):
        """Test ability to collate parts based on a specification"""
        tmpsub = copy_to_tmp()
        # copy cache tests also
        testdir = os.path.dirname(os.path.realpath(__file__))
        copy(os.path.join(testdir, 'testfiles', IGEM_FASTA_CACHE_FILE), tmpsub)
        copy(os.path.join(testdir, 'testfiles', GENBANK_CACHE_FILE), tmpsub)
        copy(os.path.join(testdir, 'testfiles', 'iGEM_SBOL2_imports.nt'), tmpsub)

        part_retrieval.collate_package(tmpsub)
        doc = sbol3.Document()
        doc.read(os.path.join(tmpsub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))
        # composite document should have 5 imported parts plus 6 parts that aren't yet imported, plus 2 templates
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}Anderson_Promoters_in_vector_ins_template', f'{pkg}Anderson_Promoters_in_vector_template',
                    'https://synbiohub.org/public/igem/BBa_J23100',
                    'https://synbiohub.org/public/igem/BBa_J23101',
                    'https://synbiohub.org/public/igem/BBa_J23102',
                    'http://parts.igem.org/pSB1C3', f'{pkg}pOpen_v4',
                    'https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115',
                    'https://synbiohub.programmingbiology.org/public/Eco1C1G1T1/LmrA',
                    f'{pkg}J23102_modified',
                    # TODO: import issues to fix:
                    f'{pkg}NM_005341_4', f'{pkg}NM_005342', f'{pkg}NM_005343'  # TODO: should these be bare or versioned?
                    }
        collated = {o.identity for o in doc.objects if isinstance(o, sbol3.Component)}
        assert collated == expected, f'Collated parts set does not match expected value: {collated}'
        sequences = [o for o in doc.objects if isinstance(o, sbol3.Sequence)]
        assert len(sequences) == 10, f'Collated document should have 10 sequences, but found {len(sequences)}'
        # Total: 13 components, 10 sequences, 4 collections, 2 CDs, 2 Activity, 1 agent, 1 attachment = 33
        assert len(doc.objects) == 33, f'Expected 33 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        comparison_file = os.path.join(testdir, 'testfiles', EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        test_file = os.path.join(tmpsub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Collated file is not identical'

if __name__ == '__main__':
    unittest.main()
