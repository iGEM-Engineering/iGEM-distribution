import os

import sbol3
import tyto

import sbol_utilities.excel_to_sbol
from sbol_utilities.helper_functions import is_plasmid
from sbol_utilities.workarounds import id_sort
from sbol_utilities.component import contained_components
from .helpers import has_SO_uri
from .package_production import BUILD_PRODUCTS_COLLECTION, DISTRIBUTION_NAMESPACE

SUMMARY_FILE = 'README.md'
"""File name for markdown summaries"""

DISTRIBUTION_SUMMARY = 'README_distribution.md'
"""File name for the distribution summary, to be located in the root directory"""


def hilite(text: str):
    """Emphasize a piece of markdown text with bold and red formatting"""
    return f' _<span style="color:red">{text}</span>_'


def generate_package_summary(package: str, doc: sbol3.Document):
    """Generate a Markdown README file summarizing package contents that is suitable for automatic display on GitHub

    :param package: package being summarized
    :param doc: package document to summarize
    :return: None
    """
    # Find the key elements
    parts_list = doc.find(sbol_utilities.excel_to_sbol.BASIC_PARTS_COLLECTION)
    build_plan = doc.find(BUILD_PRODUCTS_COLLECTION)
    if not isinstance(parts_list, sbol3.Collection):
        raise ValueError(f'Could not find parts collection in package {package}')
    if not isinstance(build_plan, sbol3.Collection):
        raise ValueError(f'Could not find build plan in package {package}')

    # compute all desired statistics
    parts_used = contained_components(build_plan)
    ids_of_parts_used = {c.identity for c in parts_used}
    unused_parts = {str(m) for m in parts_list.members} - ids_of_parts_used

    vector_parts = [m.lookup() for m in parts_list.members if is_plasmid(m.lookup())]
    non_vector_parts = [m.lookup() for m in parts_list.members if m.lookup() not in vector_parts]
    missing_seq = {m.identity for m in non_vector_parts if len(m.sequences) == 0}
    missing_vec = {m.display_id for m in vector_parts if len(m.sequences) == 0}

    # inventory parts by sequence ontology category, e.g., promoter, CDS, terminator
    so_roles = {}
    so_clusters = {}
    unknown_role_count = 0
    for c in non_vector_parts:
        so_roles[c.identity] = [tyto.SO.get_term_by_uri(t) for t in c.roles if has_SO_uri(t)]
        if not so_roles[c.identity]:
            unknown_role_count += 1
        for r in so_roles[c.identity]:
            so_clusters[r] = so_clusters.get(r, set()).union({c.identity})

    # inventory what inserts are in what vectors
    insert_vectors = {}
    for m in build_plan.members:
        c = m.lookup()
        parts = contained_components(c)
        in_vector = parts.intersection(vector_parts)
        for p in (parts - in_vector):
            insert_vectors[p] = insert_vectors.get(p, set()).union({v.display_id for v in in_vector})

    # write the README file
    summary_filename = os.path.join(package, SUMMARY_FILE)
    with open(summary_filename, 'w') as f:
        # First the package name and description
        f.write(f'# Package: {parts_list.name}\n\n')
        f.write(f'{parts_list.description}\n\n')

        # Next, summary statistics (with accompanying errors)
        f.write(f'### Summary:\n\n')
        # Part count
        missed = hilite(f'{len(missing_seq)} missing sequences') if missing_seq else ''
        f.write(f'- {len(non_vector_parts)} parts{missed}\n')
        for role in sorted(so_clusters):
            f.write(f'    - {role}: {len(so_clusters[role])}\n')
        if unknown_role_count:
            f.write(f'    - {hilite(f"unspecified role: {unknown_role_count}")}\n')
        if missing_vec:
            missed = hilite(f'{len(missing_vec)} missing sequences: {", ".join(sorted(missing_vec))}')
        else:
            missed = ''
        f.write(f'- {len(vector_parts)} vectors{missed}\n')
        # Build information
        f.write(f'- {len(build_plan.members)} samples for distribution')
        if unused_parts:
            f.write(hilite(f'{len(unused_parts)} parts not included'))
        if not build_plan.members:
            f.write(hilite(f'No samples planned to be built for distribution'))
        f.write('\n\n')  # section break

        # Finally, a list of all the parts and their UIDs
        f.write(f'### Parts:\n\n')
        for p in id_sort(non_vector_parts):
            # id / name
            f.write(f'- {p.display_id}')
            if p.name and sbol3.string_to_display_id(p.name) != p.display_id:
                f.write(f': {p.name}')
            # roles
            if so_roles.get(p.identity, None):
                f.write(f' ({", ".join(sorted(so_roles[p.identity]))})')
            if p in insert_vectors:
                f.write(f' in {", ".join(sorted(insert_vectors[p]))}')
            if p.identity in missing_seq:
                f.write(hilite(f'missing sequence, ensure file name matches Data Source ID from Excel File'))
            if p.identity in unused_parts:
                f.write(hilite(f'not included in distribution'))
            f.write('\n')
        f.write('\n')  # section break

        # add warning at the bottom
        f.write(f'_Note: automatically generated from package Excel and sequence files; do not edit_\n')


def generate_distribution_summary(root: str, doc: sbol3.Document):
    """Generate a Markdown README file summarizing distribution contents, suitable for automatic display on GitHub

    :param root: path for summary to be written to
    :param doc: package document to summarize
    :return: None
    """
    # TODO: use combinatorial derivations and expansions
    build_plan = doc.find(f'{DISTRIBUTION_NAMESPACE}/{BUILD_PRODUCTS_COLLECTION}')
    if not isinstance(build_plan, sbol3.Collection):
        raise ValueError

    summary_filename = os.path.join(root, DISTRIBUTION_SUMMARY)
    with open(summary_filename, 'w') as f:
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
