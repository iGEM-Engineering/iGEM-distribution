from __future__ import annotations
import logging
import glob
import os
import itertools

import sbol2
import sbol3
from sbol_utilities.conversion import convert2to3

from sbol_utilities.helper_functions import GENETIC_DESIGN_FILE_TYPES


def convert_package_sbol2_files(package: str) -> dict[str, str]:
    """Find all SBOL2 import files in a package directory and convert them to SBOL3 sorted n-triples

    :param package: path of package to search
    :return: dictionary mapping paths of SBOL2 inputs to SBOL3 outputs
    """
    mappings = {}

    # import SBOL2
    for file in itertools.chain(
        *(glob.glob(os.path.join(package, f'*{ext}')) for ext in GENETIC_DESIGN_FILE_TYPES['SBOL2'])
    ):
        print(f'Attempting to convert SBOL2 file {file}')
        file3 = os.path.splitext(file)[0] + '.nt'  # make an SBOL3 version of the file name
        doc2 = sbol2.Document()
        doc2.read(file)  # confirm that it is, in fact, an SBOL2 file
        doc3 = convert2to3(file)
        # check if it's valid before writing
        report = doc3.validate()
        if len(report.errors) > 0:
            logging.warning('Conversion failed: SBOL3 file has errors')
            for issue in report.errors:
                logging.warning(issue)
            continue

        # If there was a previous instance of the file, merge in all non-replaced objects
        if os.path.isfile(file3):
            merge_doc = sbol3.Document()
            merge_doc.read(file3)
            # figure out which ones to copy
            non_replaced = set(o.identity for o in merge_doc.objects) - set(o.identity for o in doc3.objects)
            for o in merge_doc.objects:
                if o.identity in non_replaced:
                    o.copy(doc3)

        print(f'Writing converted SBOL3 file to {file3}')
        doc3.write(file3, sbol3.SORTED_NTRIPLES)
        # record the conversion for later use
        mappings[file] = file3

    return mappings
