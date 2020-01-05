#


""" Implementation based on 'pkg_resources' from 'setuptools'
"""


import pkg_resources


INDENTATION = 2


def _display_conflict(distribution, requirement, depth):
    print(
        "{}{}=={}  # !!! CONFLICT {}".format(
            ' ' * INDENTATION * depth,
            distribution.project_name,
            distribution.version,
            str(requirement),
        ),
    )


def _display_cyclic(requirement, depth):
    print(
        "{}{}  # !!! CYCLIC {}".format(
            ' ' * INDENTATION * depth,
            requirement.project_name,
            str(requirement),
        ),
    )


def _display_good(distribution, requirement, depth):
    print(
        "{}{}=={}  # {}".format(
            ' ' * INDENTATION * depth,
            distribution.project_name,
            distribution.version,
            str(requirement) if requirement else '',
        ),
    )


def _display_missing(requirement, depth):
    print(
        "{}{}  # !!! MISSING {}".format(
            ' ' * INDENTATION * depth,
            requirement.project_name,
            str(requirement),
        ),
    )


def _display_forward_tree(project_req):
    _display_forward_branch(project_req, [])


def _display_forward_branch(project_req, chain):
    depth = len(chain)
    project_key = project_req.key
    if project_key in chain:
        _display_cyclic(project_req, depth)
    else:
        try:
            distribution = pkg_resources.get_distribution(project_req)
        except pkg_resources.DistributionNotFound:
            _display_missing(project_req, depth)
        except IndexError:
            # https://github.com/pypa/setuptools/issues/1677
            _display_missing(project_req, depth)
        except pkg_resources.VersionConflict:
            distribution = pkg_resources.get_distribution(project_key)
            _display_conflict(distribution, project_req, depth)
        else:
            _display_good(distribution, project_req, depth)
            try:
                dependency_reqs = sorted(
                    distribution.requires(extras=project_req.extras),
                    key=lambda req: req.key,
                )
            except pkg_resources.UnknownExtra as unknown_extra_exception:
                print(unknown_extra_exception)
            else:
                for dependency_req in dependency_reqs:
                    _display_forward_branch(
                        dependency_req,
                        chain + [distribution.key],
                    )


def _display_reverse_tree(distributions, project_requirement):
    _display_reverse_branch(distributions, project_requirement, None, [])


def _display_reverse_branch(distributions, project_req, dependency_req, chain):
    depth = len(chain)
    project_key = project_req.key
    if project_key in chain:
        _display_cyclic(project_req, depth)
    else:
        try:
            distribution = pkg_resources.get_distribution(project_req)
        except pkg_resources.DistributionNotFound:
            _display_missing(project_req, depth)
        else:
            _display_good(distribution, dependency_req, depth)
        if project_key in distributions:
            dependents = distributions[project_key]['dependents'].items()
            for (dependent_key, next_dependency_req) in sorted(dependents):
                dependent_req = pkg_resources.Requirement.parse(dependent_key)
                _display_reverse_branch(
                    distributions,
                    dependent_req,
                    next_dependency_req,
                    chain + [project_key],
                )


def _display_forward_flat(project_requirement):
    project_key = project_requirement.key
    try:
        distribution = pkg_resources.get_distribution(project_key)
    except pkg_resources.DistributionNotFound:
        print("{}  # !!! MISSING")
    else:
        print("{}=={}".format(distribution.project_name, distribution.version))
        try:
            dependency_requirements = sorted(
                distribution.requires(extras=project_requirement.extras),
                key=lambda req: req.key,
            )
        except pkg_resources.UnknownExtra as unknown_extra_exception:
            print(unknown_extra_exception)
        else:
            for dependency_requirement in dependency_requirements:
                print("# {}".format(dependency_requirement))
    print("")


def _display_reverse_flat(distributions, project_requirement):
    project_key = project_requirement.key
    try:
        distribution = pkg_resources.get_distribution(project_key)
    except pkg_resources.DistributionNotFound:
        print("{}  # !!! MISSING")
    else:
        dependents = distributions[project_key]['dependents'].items()
        for (dependent_key, dependent_req) in sorted(dependents):
            print("# {} {}".format(dependent_key, dependent_req))
        print("{}=={}".format(distribution.project_name, distribution.version))
    print("")


def _discover_distributions():
    distributions = {}
    working_set = pkg_resources.working_set
    for distribution in working_set:  # pylint: disable=not-an-iterable
        dist_key = distribution.key
        dist_val = distributions.setdefault(
            dist_key,
            {
                'dependents': {},
                'has_dependencies': False,
            },
        )
        for dependency_requirement in distribution.requires():
            dep_key = dependency_requirement.key
            dep_val = distributions.setdefault(
                dep_key,
                {
                    'dependents': {},
                    'has_dependencies': False,
                },
            )
            dep_val['dependents'][dist_key] = dependency_requirement
            dist_val['has_dependencies'] = True
    return distributions


def _select_all(distributions):
    selection = sorted(distributions.keys())
    return selection


def _select_top_level(distributions):
    selection = [
        key
        for (key, info)
        in sorted(distributions.items())
        if (
            len(info['dependents']) == 0
            or
            (key in info['dependents'] and len(info['dependents']) == 1)
        )
    ]
    return selection


def _select_bottom_level(distributions):
    selection = [
        key
        for (key, info)
        in sorted(distributions.items())
        if not info['has_dependencies']
    ]
    return selection


def main(selection, reverse, flat):
    """ Main function """
    distributions = None
    if reverse or not selection:
        distributions = _discover_distributions()

    if not selection:
        if flat:
            selection = _select_all(distributions)
        elif reverse:
            selection = _select_bottom_level(distributions)
        else:
            selection = _select_top_level(distributions)

    for item in selection:
        requirement = pkg_resources.Requirement.parse(item)
        if reverse:
            if flat:
                _display_reverse_flat(distributions, requirement)
            else:
                _display_reverse_tree(distributions, requirement)
        else:
            if flat:
                _display_forward_flat(requirement)
            else:
                _display_forward_tree(requirement)


# EOF
