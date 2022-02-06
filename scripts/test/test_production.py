import unittest
import os
import filecmp

import sbol3

from scripts.scriptutils import package_production, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME, IGEM_FASTA_CACHE_FILE, \
    NCBI_GENBANK_CACHE_FILE, IGEM_SBOL2_CACHE_FILE, BUILD_PRODUCTS_COLLECTION, DISTRIBUTION_NAMESPACE, \
    DISTRIBUTION_NAME, \
    DISTRIBUTION_FASTA, DISTRIBUTION_GENBANK, export_sbol
from scripts.test.helpers import copy_to_tmp


class TestDistributionProduction(unittest.TestCase):
    def test_collation(self):
        """Test ability to collate parts based on a specification"""
        tmp_sub = copy_to_tmp(exports=['package_specification.nt'],
                              package=['test_sequence.fasta', 'J23102-modified.fasta', 'two_sequences.gb',
                                       'BBa_J23101.nt', IGEM_FASTA_CACHE_FILE, NCBI_GENBANK_CACHE_FILE,
                                       IGEM_SBOL2_CACHE_FILE])

        package_production.collate_package(tmp_sub)
        doc = sbol3.Document()
        doc.read(os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME))
        # composite document should have the following inventory:
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        expected = {f'{pkg}Anderson_Promoters_in_vector_ins_template', f'{pkg}Anderson_Promoters_in_vector_template',
                    f'{pkg}Other_stuff_ins_template', f'{pkg}Other_stuff_template',
                    'https://synbiohub.org/public/igem/BBa_J23100',
                    'https://synbiohub.org/public/igem/BBa_J23101',
                    'https://synbiohub.org/public/igem/BBa_J23102',
                    'https://synbiohub.org/public/igem/pSB1C3',
                    'http://parts.igem.org/BBa_J364007', f'{pkg}pOpen_v4',
                    'https://www.ncbi.nlm.nih.gov/nuccore/JWYZ01000115',
                    f'{pkg}LmrA', f'{pkg}J23102_modified',
                    # TODO: should these be bare or versioned?
                    f'{pkg}NM_005341_4', f'{pkg}NM_005342', f'{pkg}NM_005343'
                    }
        collated = {o.identity for o in doc.objects if isinstance(o, sbol3.Component)}
        assert collated == expected, f'Collated parts set does not match expected value: {collated}'
        sequences = [o for o in doc.objects if isinstance(o, sbol3.Sequence)]
        assert len(sequences) == 10, f'Collated document should have 10 sequences, but found {len(sequences)}'
        # Total: 14 components, 10 sequences, 4 collections, 4 CDs, 1 Activity = 35
        assert len(doc.objects) == 35, f'Expected 35 TopLevel objects, but found {len(doc.objects)}'

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
        built = set(str(m) for m in collection.members)
        assert built == expected, f'Build set does not match expected value: {collection.members}'
        # Total: 35 from original document, plus 10 vectors, 5 vector sequences, 2x2 expansion collections,
        # 1 package build collection
        assert len(doc.objects) == 55, f'Expected 55 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, 'package-expanded.nt')
        test_file = os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Expanded file is not identical'

    def test_non_cd_build_plans(self):
        """Test that build plan works when some or all entries are not CombinatorialDerivations"""
        tmp_sub = copy_to_tmp(renames={'non_combinatorial_package.xlsx': 'test_package.xlsx'},
                              package=['BBa_J23101.nt', IGEM_FASTA_CACHE_FILE, IGEM_SBOL2_CACHE_FILE])
        pkg = 'https://github.com/iGEM-Engineering/iGEM-distribution/test_package/'
        export_sbol(tmp_sub)
        package_production.collate_package(tmp_sub)
        doc = package_production.expand_build_plan(tmp_sub)

        # check if contents of collection match expectation
        collection = doc.find(BUILD_PRODUCTS_COLLECTION)
        # 1 collection, s: 1 vectors x 4 parts, 4 individual builds
        assert len(collection.members) == 8, f'Expected 8 build products, but found {len(collection.members)}'
        # TODO: allow expansions to use short names by omitting CD name
        expected = {f'{pkg}Anderson_Promoters_in_vector_J23102_modified',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23100',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23101',
                    f'{pkg}Anderson_Promoters_in_vector_BBa_J23102',
                    f'{pkg}LmrA_in_vector',
                    f'{pkg}J23101_in_vector',
                    f'{pkg}J23102_in_vector',
                    f'{pkg}Random_Assemblage'}
        built = set(str(m) for m in collection.members)
        assert built == expected, f'Build set does not match expected value: {collection.members}'
        # Total: 31 pre-expansion, plus 4 vectors, 4 vector sequences, 1 expansion collection, 1 insert,
        # 1 package build collection
        assert len(doc.objects) == 42, f'Expected 42 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, 'non-combinatorial-package.nt')
        test_file = os.path.join(tmp_sub, EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Expanded file is not identical'

    def test_build_distribution(self):
        """Test the assembly of a complete distribution"""
        m = {os.path.join(EXPORT_DIRECTORY, 'package-expanded.nt'): os.path.join(EXPORT_DIRECTORY, SBOL_PACKAGE_NAME)}
        tmp_sub = copy_to_tmp(renames=m)
        root = os.path.dirname(tmp_sub)
        packages = [tmp_sub]
        doc = package_production.build_distribution(root, packages)

        # check if contents match expectation
        collection = doc.find(f'{DISTRIBUTION_NAMESPACE}/{BUILD_PRODUCTS_COLLECTION}')
        assert len(collection.members) == 10, f'Expected 10 build products, but found {len(collection.members)}'
        # Total: 55 from package, plus 1 total build collection
        assert len(doc.objects) == 56, f'Expected 56 TopLevel objects, but found {len(doc.objects)}'

        # check that the file is identical to expectation
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'distribution', DISTRIBUTION_NAME)
        test_file = os.path.join(root, DISTRIBUTION_NAME)
        assert filecmp.cmp(test_file, comparison_file), f'Expanded file is not identical'

    def test_synthesis_exports(self):
        """Test the export of materials for a synthesis plan"""
        remap = {os.path.join('distribution', DISTRIBUTION_NAME): DISTRIBUTION_NAME}
        tmp_sub = copy_to_tmp(renames=remap)
        root = tmp_sub  # we're just running in the package rather than true root for simplicity
        doc = sbol3.Document()
        doc.read(os.path.join(root, DISTRIBUTION_NAME))
        synth_doc = package_production.extract_synthesis_files(root, doc)

        # check if contents match expectation
        collection = synth_doc.find(BUILD_PRODUCTS_COLLECTION)
        # 10 products were planned, but only 5 have sequences
        assert len(collection.members) == 5, f'Expected 5 build products, but found {len(collection.members)}'
        # Total: 1 collection, 5x2 complete vectors and sequences, 5x2 inserts and sequences, 1x2 plasmids and sequence
        assert len(synth_doc.objects) == 23, f'Expected 23 TopLevel objects, but found {len(synth_doc.objects)}'

        # check that the files are identical to expectations
        test_dir = os.path.dirname(os.path.realpath(__file__))
        comparison_file = os.path.join(test_dir, 'test_files', 'distribution', DISTRIBUTION_FASTA)
        test_file = os.path.join(root, DISTRIBUTION_FASTA)
        assert filecmp.cmp(test_file, comparison_file), f'Exported file is not identical'
        comparison_file = os.path.join(test_dir, 'test_files', 'distribution', DISTRIBUTION_GENBANK)
        test_file = os.path.join(root, DISTRIBUTION_GENBANK)
        assert filecmp.cmp(test_file, comparison_file), f'Exported file is not identical'


if __name__ == '__main__':
    unittest.main()
