import unittest
import tempfile
import os
import filecmp
from shutil import copy

import sbol3

import scripts.scriptutils
from scripts.scriptutils import package_production, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, IGEM_FASTA_CACHE_FILE, \
    GENBANK_CACHE_FILE, IGEM_SBOL2_CACHE_FILE, BUILD_PRODUCTS_COLLECTION, DISTRIBUTION_NAMESPACE, DISTRIBUTION_NAME
from scripts.test.helpers import copy_to_tmp


class TestImportParts(unittest.TestCase):
    def test_collation(self):
        """Test ability to collate parts based on a specification"""
        tmp_sub = copy_to_tmp(exports=['package_specification.nt'],
                              package=['test_sequence.fasta', 'J23102-modified.fasta', 'two_sequences.gb',
                                       'BBa_J23101.nt', IGEM_FASTA_CACHE_FILE, GENBANK_CACHE_FILE,
                                       IGEM_SBOL2_CACHE_FILE])

        package_production.collate_package(tmp_sub)
        doc = sbol3.Document()
        doc.read(os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))
        # composite document should have 5 imported parts plus 6 parts that aren't yet imported, plus 2 templates
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}Anderson_Promoters_in_vector_ins_template', f'{pkg}Anderson_Promoters_in_vector_template',
                    f'{pkg}Other_stuff_ins_template', f'{pkg}Other_stuff_template',
                    'https://synbiohub.org/public/igem/BBa_J23100',
                    'https://synbiohub.org/public/igem/BBa_J23101',
                    'https://synbiohub.org/public/igem/BBa_J23102',
                    'http://parts.igem.org/pSB1C3', f'{pkg}pOpen_v4',
                    'https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115',
                    'https://synbiohub.programmingbiology.org/public/Eco1C1G1T1/LmrA',
                    f'{pkg}J23102_modified',
                    # TODO: should these be bare or versioned?
                    f'{pkg}NM_005341_4', f'{pkg}NM_005342', f'{pkg}NM_005343'
                    }
        collated = {o.identity for o in doc.objects if isinstance(o, sbol3.Component)}
        assert collated == expected, f'Collated parts set does not match expected value: {collated}'
        sequences = [o for o in doc.objects if isinstance(o, sbol3.Sequence)]
        assert len(sequences) == 10, f'Collated document should have 10 sequences, but found {len(sequences)}'
        # Total: 13 components, 10 sequences, 4 collections, 4 CDs, 2 Activity, 1 agent, 1 attachment = 33
        assert len(doc.objects) == 37, f'Expected 37 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        test_file = os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Collated file is not identical'

    def test_build_plan(self):
        """Test ability to collate parts based on a specification"""
        tmp_sub = copy_to_tmp(exports=[SBOL_PACKAGE_NAME])
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        doc = package_production.expand_build_plan(tmp_sub)

        # check if contents of collection match expectation
        collection = doc.find(BUILD_PRODUCTS_COLLECTION)
        # 2 collections: 2 vectors x 4 parts, 1 vector x 2 parts
        assert len(collection.members) == 10, f'Expected 10 build products, but found {len(collection.members)}'
        # TODO: allow expansions to use short names by omitting CD name
        expected = {f'{pkg}Anderson_Promoters_in_vector_J23102_modified_pSB1C3',
                    f'{pkg}Anderson_Promoters_in_vector_J23102_modified_pOpen_v4',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23100_pSB1C3',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23100_pOpen_v4',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23101_pSB1C3',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23101_pOpen_v4',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23102_pSB1C3',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23102_pOpen_v4',
                    f'{pkg}Other_stuff_LmrA',
                    f'{pkg}Other_stuff_JWYZ01000115'}
        assert set(str(m) for m in collection.members) == expected, f'Build set does not match expected value: {collection.members}'
        # Total: 37 from original document, plus 10 vectors, 2x2 expansion collections, 1 package build collection
        assert len(doc.objects) == 52, f'Expected 52 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, 'package-expanded.nt')
        test_file = os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Expanded file is not identical'

    def test_build_distribution(self):
        """Test the assembly of a complete distribution"""
        rm = {os.path.join(EXPORT_DIRECTORY, 'package-expanded.nt'): os.path.join(EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)}
        tmp_sub = copy_to_tmp(renames=rm)
        root = os.path.dirname(tmp_sub)
        packages = [tmp_sub]
        doc = package_production.build_distribution(root,packages)

        # check if contents match expectation
        collection = doc.find(f'{DISTRIBUTION_NAMESPACE}/{BUILD_PRODUCTS_COLLECTION}')
        assert len(collection.members) == 10, f'Expected 10 build products, but found {len(collection.members)}'
        # Total: 52 from package, plus 1 total build collection
        assert len(doc.objects) == 53, f'Expected 53 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'distribution', DISTRIBUTION_NAME)
        test_file = os.path.join(root, DISTRIBUTION_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Expanded file is not identical'


if __name__ == '__main__':
    unittest.main()
