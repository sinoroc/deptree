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


def _display_missing_reverse(requirement, depth):
    print(
        "{}{}  # MISSING".format(
            ' ' * INDENTATION * depth,
            requirement.project_name,
        ),
    )


def _display(distributions, requirement, chain):
    depth = len(chain)
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
        if distribution.key in chain:
            _display_cyclic(distribution, requirement, depth)
        else:
            _display_good(distribution, requirement, depth)
            try:
                dependencies = distribution.requires(extras=requirement.extras)
            except pkg_resources.UnknownExtra as exception:
                print(exception)
            else:
                sorted_dependency_keys = sorted([
                    dependency.key
                    for dependency
                    in dependencies
                ])
                all_deps = distributions[distribution.key]['dependencies']
                for dependency_key in sorted_dependency_keys:
                    dependency_requirement = all_deps[dependency_key]
                    _display(
                        distributions,
                        dependency_requirement,
                        chain + [distribution.key],
                    )


def _display_reverse(distributions, project_req, dependency_req, chain):
    depth = len(chain)
    try:
        project_dist = pkg_resources.get_distribution(project_req)
    except pkg_resources.DistributionNotFound:
        _display_missing_reverse(project_req, depth)
    else:
        if project_dist.key in chain:
            _display_cyclic(project_dist, dependency_req, depth)
        else:
            if dependency_req:
                try:
                    pkg_resources.get_distribution(dependency_req)
                except pkg_resources.VersionConflict:
                    _display_conflict(project_dist, dependency_req, depth)
                else:
                    _display_good(project_dist, dependency_req, depth)
            else:
                _display_good(project_dist, '', depth)
            dependents = distributions[project_dist.key]['dependents']
            for (dependent_key, dependent_req) in sorted(dependents.items()):
                _display_reverse(
                    distributions,
                    dependent_key,
                    dependent_req,
                    chain + [project_dist.key],
                )


def _discover_distributions():
    working_set = pkg_resources.working_set
    distributions = {}
    for distribution in working_set:  # pylint: disable=not-an-iterable
        key = distribution.key
        if key not in distributions:
            distributions[key] = {
                'dependencies': {},
                'dependents': {},
            }
        distributions[key]['installed'] = True
        for requirement in distribution.requires(extras=distribution.extras):
            distributions[key]['dependencies'][requirement.key] = requirement
            if requirement.key not in distributions:
                distributions[requirement.key] = {
                    'dependencies': {},
                    'dependents': {},
                    'installed': False,
                }
            distributions[requirement.key]['dependents'][key] = requirement
    return distributions


def _select_top_level(distributions):
    selection = [
        key
        for (key, info)
        in sorted(distributions.items())
        if not info['dependents']
    ]
    return selection


def _select_bottom_level(distributions):
    selection = [
        key
        for (key, info)
        in sorted(distributions.items())
        if info['installed'] and not info['dependencies']
    ]
    return selection


def main(selection, reverse):
    """ Main function """
    distributions = _discover_distributions()
    if not selection:
        if reverse:
            selection = _select_bottom_level(distributions)
        else:
            selection = _select_top_level(distributions)
    for item in selection:
        requirement = pkg_resources.Requirement.parse(item)
        if reverse:
            _display_reverse(distributions, requirement, None, [])
        else:
            _display(distributions, requirement, [])


# EOF
