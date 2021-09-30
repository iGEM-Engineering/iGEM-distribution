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
    inserts = {f for f in set(component.features)-subvectors if isinstance(f, sbol3.SubComponent)}
    if len(inserts) == 1:
        return inserts.pop().instance_of.lookup()
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
