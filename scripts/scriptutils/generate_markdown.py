import os

import sbol3
import tyto

import sbol_utilities.excel_to_sbol
from sbol_utilities.helper_functions import id_sort

SUMMARY_FILE = 'README.md'  # markdown for summary

def generate_package_summary(package: str, doc: sbol3.Document):
    """Generate a Markdown README file summarizing package contents that is suitable for automatic display on GitHub

    :param package: package being summarized
    :param doc: package document to summarize
    :return: None
    """
    # TODO: use combinatorial derivations and expansions
    parts_list = doc.find(sbol_utilities.excel_to_sbol.BASIC_PARTS_COLLECTION)
    if not isinstance(parts_list,sbol3.Collection):
        raise ValueError

    summary_filename = os.path.join(package,SUMMARY_FILE)
    with open(summary_filename,'w') as f:
        # First the package name and description
        f.write(f'# Package: {parts_list.name}\n\n')
        f.write(f'{parts_list.description}\n\n')

        # Next, statistics and errors
        f.write(f'### Summary:\n\n')
        f.write(f'- {len(parts_list.members)} parts\n')
        missing_seq = [str(m) for m in parts_list.members if len(m.lookup().sequences)==0]
        f.write(f'- {len(missing_seq)} are missing sequences\n')
        # TODO: inventory the common types of parts, e.g., promoter, CDS, terminator
        f.write('\n')  # section break

        # Finally, a list of all the parts and their UIDs
        f.write(f'### Parts:\n\n')
        for p in id_sort(m.lookup() for m in parts_list.members):
            f.write(f'- {p.display_id}')
            if p.name and sbol_utilities.excel_to_sbol.string_to_display_id(p.name) != p.display_id:
                f.write(f': {p.name}')
            # TODO: more principled handling of role lookup
            SO_roles = [tyto.SO.get_term_by_uri(t) for t in p.roles if t.startswith("https://identifiers.org/SO") or t.startswith("http://identifiers.org/so/SO")]
            if SO_roles:
                f.write(f' ({", ".join(SO_roles)})')
            if p.identity in missing_seq:
                f.write(f' _<span style="color:red">missing sequence</span>_')
            f.write('\n')
        f.write('\n')  # section break

        # add warning at the bottom
        f.write(f'_Note: automatically generated from package Excel and sequence files; do not edit_\n')
