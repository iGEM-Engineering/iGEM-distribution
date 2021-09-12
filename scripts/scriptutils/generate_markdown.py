import os

import sbol3
import tyto

import sbol_utilities.excel_to_sbol
from sbol_utilities.helper_functions import id_sort, is_plasmid
from .helpers import contained_components, has_SO_uri
from .package_production import BUILD_PRODUCTS_COLLECTION, DISTRIBUTION_NAMESPACE

SUMMARY_FILE = 'README.md'
"""File name for markdown summaries"""

DISTRIBUTION_SUMMARY = 'README_distribution.md'
"""File name for the distribution summary, to be located in the root directory"""

def hilite(text: str):
    """Emphasize a piece of markdown text with bold and red formatting"""
    return f' **<span style="color:red">{text}</span>**'

def generate_package_summary(package: str, doc: sbol3.Document):
    """Generate a Markdown README file summarizing package contents that is suitable for automatic display on GitHub

    :param package: package being summarized
    :param doc: package document to summarize
    :return: None
    """
    # TODO: use combinatorial derivations and expansions
    # Find the key elements
    parts_list = doc.find(sbol_utilities.excel_to_sbol.BASIC_PARTS_COLLECTION)
    build_plan = doc.find(BUILD_PRODUCTS_COLLECTION)
    if not isinstance(parts_list, sbol3.Collection):
        raise ValueError(f'Could not find parts collection in package {package}')
    if not isinstance(build_plan, sbol3.Collection):
        raise ValueError(f'Could not find build plan in package {package}')

    # compute all required statistics
    parts_used = contained_components(build_plan)
    ids_of_parts_used = {c.identity for c in parts_used}
    unused_parts = {str(m) for m in parts_list.members} - ids_of_parts_used

    # write the README file
    summary_filename = os.path.join(package,SUMMARY_FILE)
    with open(summary_filename,'w') as f:
        # First the package name and description
        f.write(f'# Package: {parts_list.name}\n\n')
        f.write(f'{parts_list.description}\n\n')

        # Next, statistics and errors
        f.write(f'### Summary:\n\n')
        # Part count
        # TODO: separate parts from vectors
        vectors = [m for m in parts_list.members if is_plasmid(m.lookup())]
        non_vectors = [m for m in parts_list.members if m not in vectors]
        missing_seq = [str(m) for m in non_vectors if len(m.lookup().sequences) == 0]
        missing_vec = [str(m) for m in vectors if len(m.lookup().sequences) == 0]
        missings = f' **<span style="color:red">{len(missing_seq)} missing sequences</span>**' if missing_seq else ''
        f.write(f'- {len(non_vectors)} parts{missings}\n')
        missings = f' **<span style="color:red">{len(missing_vec)} missing sequences</span>**' if missing_vec else ''
        f.write(f'- {len(vectors)} vectors{missings}\n')
        # TODO: inventory the common types of parts, e.g., promoter, CDS, terminator
        # Build information
        f.write(f'- {len(build_plan.members)} samples for distribution')
        if unused_parts:
            f.write(hilite(f'{len(unused_parts)} parts not included'))
        if not build_plan.members:
            f.write(hilite(f'No samples planned to be built for distribution'))
        f.write('\n\n')  # section break

        # Finally, a list of all the parts and their UIDs
        f.write(f'### Parts:\n\n')
        for p in id_sort(m.lookup() for m in parts_list.members):
            f.write(f'- {p.display_id}')
            if p.name and sbol_utilities.excel_to_sbol.string_to_display_id(p.name) != p.display_id:
                f.write(f': {p.name}')
            # TODO: more principled handling of role lookup
            #SO_roles = []
            SO_roles = [tyto.SO.get_term_by_uri(t) for t in p.roles if has_SO_uri(t)]
            if SO_roles:
                f.write(f' ({", ".join(SO_roles)})')
            if p.identity in missing_seq or p.identity in missing_vec:
                f.write(hilite(f'missing sequence'))
            if p.identity in unused_parts:
                f.write(hilite(f'not included in distribution'))
            f.write('\n')
        f.write('\n')  # section break

        # add warning at the bottom
        f.write(f'_Note: automatically generated from package Excel and sequence files; do not edit_\n')


def generate_distribution_summary(root: str, doc: sbol3.Document):
    """Generate a Markdown README file summarizing distribution contents that is suitable for automatic display on GitHub

    :param root: path for summary to be written to
    :param doc: package document to summarize
    :return: None
    """
    # TODO: use combinatorial derivations and expansions
    build_plan = doc.find(f'{DISTRIBUTION_NAMESPACE}/{BUILD_PRODUCTS_COLLECTION}')
    if not isinstance(build_plan,sbol3.Collection):
        raise ValueError

    summary_filename = os.path.join(root,DISTRIBUTION_SUMMARY)
    with open(summary_filename,'w') as f:
        # First the package name and description
        f.write(f'# Distribution Summary\n\n')

        # Build information
        f.write(f'- {len(build_plan.members)} samples planned for distribution')
        f.write('\n\n')  # section break

        # List of all the built samples and their UIDs
        f.write(f'### Parts:\n\n')
        for p in id_sort(m.lookup() for m in build_plan.members):
            f.write(f'- {p.display_id}\n')
        f.write('\n')  # section break

        # add warning at the bottom
        f.write(f'_Note: automatically generated from distribution SBOL file; do not edit_\n')
