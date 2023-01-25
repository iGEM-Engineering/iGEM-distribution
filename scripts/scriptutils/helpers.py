from __future__ import annotations
import math
from collections.abc import Iterable
from itertools import count

import sbol3
import tyto
from sbol_utilities.helper_functions import is_plasmid


def vector_to_insert(component: sbol3.Component) -> sbol3.Component:
    """If the component is a vector, peel it open to find the sub-component that is not the vector portion
    If the component is not a vector, return it directly
    Throws a ValueError if the component is a vector but does not have precisely one insert

    :param component: SBOL3 component to extract from
    :return: component if not vector; otherwise the vector
    """
    # is either the component or any feature thereof a vector? If not, then return component
    subvectors = {f for f in component.features if is_plasmid(f)}
    if len(subvectors) == 0 and not is_plasmid(component):
        return component
    # otherwise, if there's precisely one non-vector subcomponent, return the Component it points to
    inserts = {f for f in set(component.features) - subvectors if isinstance(f, sbol3.SubComponent)}
    if len(inserts) == 1:
        return inserts.pop().instance_of.lookup()
    elif len(inserts) == 0:
        return component  # Does not appear to be a vector
    else:
        raise ValueError(f'Vector should have one insert, but found {len(inserts)}: {component.identity}')


# TODO: remove this TYTO extension methods after resolution of issue https://github.com/SynBioDex/tyto/issues/33
def has_SO_uri(uri: str) -> bool:
    """Test if a given URI is in the ontology (effectively an exception-checking wrapper around get_term_by_uri)

    :param ontology: Ontology to check for term containment
    :param str: URI to look up
    :return: true if this is a URI in the
    """
    if not (uri.startswith("https://identifiers.org/SO") or uri.startswith("http://identifiers.org/so/SO")):
        return False
    try:
        tyto.SO.get_term_by_uri(uri)
        return True
    except LookupError:
        return False


def remove_duplicate_prefix(name: str) -> str:
    """Remove extra prefixes common in insert names
    TODO: remove on resolution of https://github.com/iGEM-Engineering/iGEM-distribution/issues/161
    :param name: name to sanitize
    :return sanitized name
    """
    components = name.split('_')
    # check from largest possible repeated block to smallest
    for i in reversed(range(1, math.floor(len(components) / 2) + 1)):
        # Check if there is a repeated block at the front
        if components[0:i] == components[i:(2 * i)]:
            if components[2 * i] == 'ins':  # also remove insertion markers
                ins_less = "_".join(name.split("_")[0:i] + [name.split("_", (2 * i) + 1)[-1]])
                return ins_less
            else:
                return name.split('_', i)[-1]
    return name


def truncate_by_underscores(name: str, max_len: int) -> str:
    """Shorten a name by lopping off front chunks, breaking it at underscores if possible

    :param name: name to truncate
    :param max_len: cutoff size
    :return: truncated name
    """
    while len(name) > max_len:
        components = name.split('_', 1)
        if len(components) > 1:
            name = components[-1]
        else:
            name = name[(len(name) - max_len):]
    return name


def sanitize_identifiers_for_synthesis(components: Iterable[sbol3.Component], max_len: int = 32) \
        -> dict[sbol3.Component, str]:
    """Generate a dictionary of sanitized names for elements in a synthesis order that are
    acceptable for a synthesis provides and contain no duplicates.

    :param components: Collection of components to generate sanitized names for
    :param max_len: maximum length of a sanitized name
    :return: dictionary mapping each insert to its sanitized name
    """

    synthesis_names = {}
    for c in components:
        synthesis_name = c.display_id
        # strip and duplicate headers and "_ins" sections
        synthesis_name = remove_duplicate_prefix(synthesis_name)
        # truncate if necessary, dropping front portion
        synthesis_name = truncate_by_underscores(synthesis_name, max_len)
        # remove any underscore prefix
        synthesis_name = synthesis_name.lstrip('_')
        # insert as a non-conflicting name
        if synthesis_name in synthesis_names.values():
            for i in count(2):
                alt_name = truncate_by_underscores(f'{synthesis_name}_{i}', max_len).lstrip('_')
                if alt_name not in synthesis_names.values():
                    synthesis_name = alt_name
                    break
        synthesis_names[c] = synthesis_name
    # return completed collection
    return synthesis_names
