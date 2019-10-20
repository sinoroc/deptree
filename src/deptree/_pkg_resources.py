#


""" Implementation based on 'pkg_resources' from 'setuptools'
"""


import pkg_resources


INDENTATION = 2


def _display_conflict(distribution, requirement, depth):
    print(
        "{}{}=={}  # CONFLICT {}".format(
            ' ' * INDENTATION * depth,
            distribution.project_name,
            distribution.version,
            requirement,
        ),
    )


def _display_cyclic(distribution, requirement, depth):
    print(
        "{}{}=={}  # CYCLIC {}".format(
            ' ' * INDENTATION * depth,
            distribution.project_name,
            distribution.version,
            requirement,
        ),
    )


def _display_good(distribution, requirement, depth):
    print(
        "{}{}=={}  # {}".format(
            ' ' * INDENTATION * depth,
            distribution.project_name,
            distribution.version,
            requirement,
        ),
    )


def _display_missing(requirement, depth):
    print(
        "{}{}  # MISSING {}".format(
            ' ' * INDENTATION * depth,
            requirement.project_name,
            requirement,
        ),
    )


def _display(requirement, depth, seen):
    try:
        distribution = pkg_resources.get_distribution(requirement)
    except pkg_resources.VersionConflict:
        distribution = pkg_resources.get_distribution(requirement.key)
        _display_conflict(distribution, requirement, depth)
    except pkg_resources.DistributionNotFound:
        _display_missing(requirement, depth)
    except IndexError:
        # https://github.com/pypa/setuptools/issues/1677
        _display_missing(requirement, depth)
    else:
        if distribution.key in seen:
            _display_cyclic(distribution, requirement, depth)
        else:
            _display_good(distribution, requirement, depth)
            try:
                dependencies = distribution.requires(extras=requirement.extras)
            except pkg_resources.UnknownExtra as exception:
                print(exception)
            else:
                for dependency_requirement in dependencies:
                    _display(
                        dependency_requirement,
                        depth + 1,
                        seen + [requirement.key],
                    )


def _get_top_level():
    working_set = pkg_resources.working_set
    distributions = {}
    for distribution in working_set:  # pylint: disable=not-an-iterable
        distributions.setdefault(distribution.key, True)  # if not exist yet
        for dependency in distribution.requires():
            distributions[dependency.key] = False
    top_level = [
        key
        for (key, is_top_level) in distributions.items()
        if is_top_level
    ]
    return top_level


def main(selection):
    """ Main function """
    if not selection:
        selection = _get_top_level()
    for item in selection:
        requirement = pkg_resources.Requirement.parse(item)
        _display(requirement, 0, [])


# EOF
