import re
from copy import copy


def is_iterable(obj):
    """Portable way to check that an object is iterable"""
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def resolve_pattern(pattern, attr_source):
    """Resolve a string pattern using values from an attribute source. If one attribute is an iterable (and not a
    string) the pattern will be resolved once for each value in the iterable.

    Parameters
    ----------
    pattern: str
        A string pattern such as '{placeholder1}/___aa__{placeholder2).stg'.
    attr_source: object
        An object with attributes matching the names of the placeholders in the patterns.

    Returns
    -------
    resolved: iterable
        The list of resolved patterns
    """
    matches = re.findall(r"{([^\}]+)}", pattern)
    attr_dict = {match: getattr(attr_source, match, "_") for match in matches}

    # remaining attributes to fill in the pattern
    remaining = set(attr_dict.keys())
    patterns = [pattern]
    for attr, values in attr_dict.items():
        remaining.remove(attr)
        resolved = list()
        if isinstance(values, str) or not is_iterable(values):
            values = [values]
        format_params = {a: "{" + a + "}" for a in remaining}
        for v in values:
            for p in patterns:
                format_params = copy(format_params)
                format_params[attr] = v
                resolved.append(p.format(**format_params))
        patterns = resolved

    return patterns