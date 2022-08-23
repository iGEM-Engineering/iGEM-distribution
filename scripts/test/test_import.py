import unittest
import os
import filecmp

from scripts.scriptutils import part_retrieval, IGEM_FASTA_CACHE_FILE, NCBI_GENBANK_CACHE_FILE, \
    convert_package_sbol2_files, IGEM_SBOL2_CACHE_FILE, export_sbol, OTHER_FASTA_CACHE_FILE, OTHER_GENBANK_CACHE_FILE, \
    collate_package, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME
from scripts.test.helpers import copy_to_tmp


class TestImportParts(unittest.TestCase):
    def test_inventory(self):
        """Test ability to take inventory of parts already in a directory"""
        tmp_sub = copy_to_tmp(package=['test_sequence.fasta', 'J23102-modified.fasta', 'two_sequences.gb',
                                       'BBa_J23101.nt'])
        inventory = part_retrieval.package_parts_inventory(tmp_sub)
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
        tmp_sub = copy_to_tmp(
            package=['test_sequence.fasta', 'J23102-modified.fasta', 'two_sequences.gb', 'BBa_J23101.nt'],
            exports=['package_specification.nt']
        )

        # first round of import should obtain all but two missing parts
        retrieved = part_retrieval.import_parts(tmp_sub)
        assert len(retrieved) == 5
        expected = ['https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1', 'http://parts.igem.org/BBa_J364007',
                    'http://parts.igem.org/J23100', 'http://parts.igem.org/J23102', 'http://parts.igem.org/pSB1C3']
        assert retrieved == expected, f'Retrieved parts list does not match expected value: {retrieved}'
        test_dir = os.path.dirname(os.path.realpath(__file__))
        # convert the retrieved SBOL2 file to SBOL3
        convert_package_sbol2_files(tmp_sub)
        targets = [IGEM_FASTA_CACHE_FILE, NCBI_GENBANK_CACHE_FILE, IGEM_SBOL2_CACHE_FILE]
        for t in targets:
            test_file = os.path.join(tmp_sub, t)
            comparison_file = os.path.join(test_dir, 'test_files', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

        # running import again should download nothing new but continue with just the two missing parts
        retrieved = part_retrieval.import_parts(tmp_sub)
        assert len(retrieved) == 0
        for t in targets:
            test_file = os.path.join(tmp_sub, t)
            comparison_file = os.path.join(test_dir, 'test_files', t)
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

    def test_all_import_types(self):
        """Test ability to retrieve parts from all different import sources"""
        tmp_sub = copy_to_tmp(package=['J23102-modified.fasta'], renames={'imports_test.xlsx': 'test_package.xlsx'})
        export_sbol(tmp_sub)

        # first round of import should obtain all but one missing part
        retrieved = part_retrieval.import_parts(tmp_sub)
        # assert len(retrieved) == 7  # all but the local file and LCP SynBioHub
        github_prefix = ('https://raw.githubusercontent.com/'
                         'iGEM-Engineering/iGEM-distribution/develop/scripts/test/test_files')
        expected = ['https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115_1',  # NCBI
                    'http://parts.igem.org/BBa_J364007',  # iGEM FASTA
                    'http://parts.igem.org/J23100',  # iGEM SynBioHub
                    'http://sevahub.es/public/Canonical/cd_OriT',  # SEVA
                    'http://sevahub.es/public/Canonical/lacZ_pUC19',  # any SynBioHub, not starting w. synbiohub
                    'https://freegenes.github.io/genbank/BBF10K_000152',  # any GenBank URL
                    f'{github_prefix}/BBa_J23101', f'{github_prefix}/imports/second_fasta',
                    f'{github_prefix}/imports/second_genbank']  # any FASTA URL
        assert retrieved == expected, f'Retrieved parts list does not match expected value: {retrieved}'
        test_dir = os.path.dirname(os.path.realpath(__file__))
        # convert the retrieved SBOL2 file to SBOL3
        convert_package_sbol2_files(tmp_sub)
        targets = {IGEM_FASTA_CACHE_FILE: os.path.join('imports', 'imports_test_igem.fasta'),
                   NCBI_GENBANK_CACHE_FILE: os.path.join('imports', 'imports_test_ncbi.gb'),
                   'BBF10K_000152.gb': os.path.join('imports', 'BBF10K_000152.gb'),
                   'second_genbank.gb': os.path.join('imports', 'second_genbank.gb'),
                   OTHER_FASTA_CACHE_FILE: os.path.join('imports', 'imports_test.fasta'),
                   IGEM_SBOL2_CACHE_FILE: os.path.join('imports', 'imports_test.nt')}
        for t in targets:
            test_file = os.path.join(tmp_sub, t)
            comparison_file = os.path.join(test_dir, 'test_files', targets[t])
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

        # running import again should download nothing new
        retrieved = part_retrieval.import_parts(tmp_sub)
        assert len(retrieved) == 0
        for t in targets:
            test_file = os.path.join(tmp_sub, t)
            comparison_file = os.path.join(test_dir, 'test_files', targets[t])
            assert filecmp.cmp(test_file, comparison_file), f'Parts cache file {t} is not identical'

        # make sure we get appropriate integration in the package:
        collate_package(tmp_sub)
        test_file = os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        comparison_file = os.path.join(test_dir, 'test_files', 'imports', SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Integated package is not identical'


if __name__ == '__main__':
    unittest.main()
