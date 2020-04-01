#


""" Implementation based on 'pkg_resources' from 'setuptools'
"""


import copy
import enum

import pkg_resources


INDENTATION = 2


def _display_conflict(distribution, requirement, depth=0):
    print(
        "{}{}=={}  # !!! CONFLICT {}".format(
            ' ' * INDENTATION * depth,
            distribution['project_name'],
            distribution['version'],
            requirement['str'],
        ),
    )


def _display_cyclic(distribution, requirement, depth=0):
    print(
        "{}{}  # !!! CYCLIC {}".format(
            ' ' * INDENTATION * depth,
            distribution['project_name'],
            requirement['str'],
        ),
    )


def _display_flat(distribution):
    print(
        "{}=={}".format(
            distribution['project_name'],
            distribution['version'],
        ),
    )


def _display_flat_dependency(requirement):
    print("# {}".format(requirement['str']))


def _display_flat_dependent(distribution, requirement):
    print("# {}: {}".format(distribution['project_name'], requirement['str']))


def _display_good(distribution, requirement, depth=0):
    print(
        "{}{}=={}  # {}".format(
            ' ' * INDENTATION * depth,
            distribution['project_name'],
            distribution['version'],
            requirement['str'],
        ),
    )


def _display_missing(project_key, requirement, depth=0):
    print(
        "{}{}  # !!! MISSING {}".format(
            ' ' * INDENTATION * depth,
            project_key,
            requirement['str'],
        ),
    )


def _display_unknown(project_label, requirement, depth=0):
    print(
        "{}{}  # !!! UNKNOWN {}".format(
            ' ' * INDENTATION * depth,
            project_label,
            requirement['str'],
        ),
    )


def _display_forward_tree(distributions, requirement, chain):
    depth = len(chain)
    project_key = requirement['dependency_project_key']
    distribution = distributions.get(project_key, None)
    if project_key in chain:
        _display_cyclic(distribution, requirement, depth)
    else:
        if not distribution:
            _display_unknown(project_key, requirement, depth)
        elif not distribution['found']:
            _display_missing(project_key, requirement, depth)
        else:
            if distribution['conflicts']:
                _display_conflict(distribution, requirement, depth)
            else:
                _display_good(distribution, requirement, depth)
            #
            for dependency in distribution['dependencies'].values():
                _display_forward_tree(
                    distributions,
                    dependency,
                    chain + [project_key]
                )


def _display_reverse_tree(
        distributions,
        requirement,
        chain,
):
    depth = len(chain)
    project_key = requirement['dependent_project_key']
    distribution = distributions.get(project_key, None)
    if project_key in chain:
        _display_cyclic(distribution, requirement, depth)
    else:
        if not distribution:
            _display_unknown(project_key, requirement, depth)
        else:
            if not distribution['found']:
                _display_missing(project_key, requirement, depth)
            elif distribution['conflicts']:
                _display_conflict(distribution, requirement, depth)
            else:
                _display_good(distribution, requirement, depth)
            #
            for dependent_key in distribution['dependents']:
                dependent_distribution = distributions[dependent_key]
                dependencies = dependent_distribution['dependencies']
                dependency_requirement = dependencies[project_key]
                _display_reverse_tree(
                    distributions,
                    dependency_requirement,
                    chain + [project_key],
                )


def _display_forward_flat(distributions, requirement):
    project_key = requirement['dependency_project_key']
    distribution = distributions.get(project_key, None)
    if not distribution:
        _display_unknown(project_key, requirement)
    else:
        if not distribution['found']:
            _display_missing(project_key, requirement)
        elif distribution['conflicts']:
            _display_conflict(distribution, requirement)
        else:
            _display_flat(distribution)
        #
        for dependency_requirement in distribution['dependencies'].values():
            _display_flat_dependency(dependency_requirement)
    #
    print("")


def _display_reverse_flat(distributions, requirement):
    project_key = requirement['dependent_project_key']
    distribution = distributions.get(project_key, None)
    if not distribution:
        _display_unknown(project_key, requirement)
    else:
        for dependent_key in distribution['dependents']:
            dependent_distribution = distributions[dependent_key]
            dependencies = dependent_distribution['dependencies']
            dependency_requirement = dependencies[project_key]
            _display_flat_dependent(
                distributions[dependent_key],
                dependency_requirement,
            )
        #
        if not distribution['found']:
            _display_missing(project_key, requirement)
        elif distribution['conflicts']:
            _display_conflict(distribution, requirement)
        else:
            _display_flat(distribution)
    #
    print("")


def _transform_requirement(dependent_project_key, requirement_):
    requirement = {
        'dependent_project_key': dependent_project_key,
        'dependency_project_key': requirement_.key if requirement_ else None,
        'extras': requirement_.extras if requirement_ else [],
        'str': str(requirement_) if requirement_ else '-',
    }
    return requirement


def _make_requirement(project_key, is_reverse):
    requirement = None
    if is_reverse:
        requirement = _transform_requirement(project_key, None)
    else:
        requirement_ = pkg_resources.Requirement.parse(project_key)
        requirement = _transform_requirement(None, requirement_)
    return requirement


def _select_flat_forward(distributions, requirement, selection, chain):
    project_key = requirement['dependency_project_key']
    distribution = distributions.get(project_key, None)
    #
    if project_key not in selection:
        selection[project_key] = _make_requirement(project_key, False)
    #
    if project_key not in chain:
        if distribution:
            for dependency in distribution['dependencies'].values():
                _select_flat_forward(
                    distributions,
                    dependency,
                    selection,
                    chain + [project_key],
                )


def _select_flat_reverse(distributions, requirement, selection, chain):
    project_key = requirement['dependent_project_key']
    distribution = distributions.get(project_key, None)
    #
    if project_key not in selection:
        selection[project_key] = _make_requirement(project_key, True)
    #
    if project_key not in chain:
        if distribution:
            for dependent_key in distribution['dependents']:
                dependent_distribution = distributions[dependent_key]
                dependencies = dependent_distribution['dependencies']
                dependency_requirement = dependencies[project_key]
                _select_flat_reverse(
                    distributions,
                    dependency_requirement,
                    selection,
                    chain + [project_key],
                )


def _select_flat(distributions, is_reverse, preselection, selection):
    for project_key in preselection:
        requirement = preselection[project_key]
        if is_reverse:
            _select_flat_reverse(
                distributions,
                requirement,
                selection,
                [],
            )
        else:
            _select_flat_forward(
                distributions,
                requirement,
                selection,
                [],
            )


def _select_bottom(distributions, selection) -> None:
    for distribution_key in distributions:
        if distribution_key not in selection:
            distribution = distributions[distribution_key]
            if not distribution['dependencies']:
                selection[distribution_key] = (
                    _make_requirement(distribution_key, True)
                )


def _select_top(distributions, selection) -> None:
    for distribution_key in distributions:
        if distribution_key not in selection:
            distribution = distributions[distribution_key]
            if not distribution['dependents']:
                selection[distribution_key] = (
                    _make_requirement(distribution_key, False)
                )


class _SelectType(enum.Enum):
    ALL = enum.auto()
    BOTTOM = enum.auto()
    FLAT = enum.auto()
    USER = enum.auto()
    TOP = enum.auto()


def _get_select_type(has_preselection, is_flat, is_reverse) -> _SelectType:
    select_type = _SelectType.USER
    if not has_preselection:
        if is_flat:
            select_type = _SelectType.ALL
        elif is_reverse:
            select_type = _SelectType.BOTTOM
        else:
            select_type = _SelectType.TOP
    elif is_flat:
        select_type = _SelectType.FLAT
    return select_type


def _discover_distributions(preselection, is_reverse, is_flat):
    default_dist_dict = {
        'conflicts': [],
        'dependencies': {},
        'dependents': [],
        'found': False,
        'project_name': None,
        'version': None,
    }
    distributions = {}
    selection = copy.deepcopy(preselection)
    #
    select_type = _get_select_type(bool(preselection), is_flat, is_reverse)
    #
    for distribution_ in list(pkg_resources.working_set):
        project_key = distribution_.key
        distribution = distributions.setdefault(
            project_key,
            copy.deepcopy(default_dist_dict),
        )
        distribution['found'] = True
        distribution['project_name'] = distribution_.project_name
        distribution['version'] = distribution_.version
        #
        extras = (
            preselection[project_key]['extras']
            if project_key in preselection
            else []
        )
        #
        if select_type == _SelectType.ALL and project_key not in selection:
            selection[project_key] = _make_requirement(project_key, is_reverse)
        #
        for requirement_ in distribution_.requires(extras=extras):
            requirement = _transform_requirement(project_key, requirement_)
            dependency_key = requirement['dependency_project_key']
            dependency = distributions.setdefault(
                dependency_key,
                copy.deepcopy(default_dist_dict),
            )
            dependency['dependents'].append(project_key)
            distribution['dependencies'][dependency_key] = requirement
            #
            try:
                pkg_resources.get_distribution(requirement_)
            except pkg_resources.VersionConflict:
                dependency['conflicts'].append(project_key)
            except pkg_resources.DistributionNotFound:
                pass
            #
            if (
                    select_type == _SelectType.ALL
                    and dependency_key not in selection
            ):
                selection[dependency_key] = _make_requirement(
                    dependency_key,
                    is_reverse,
                )
    #
    if select_type in (_SelectType.FLAT,):
        _select_flat(distributions, is_reverse, preselection, selection)
    elif select_type == _SelectType.BOTTOM:
        _select_bottom(distributions, selection)
    elif select_type == _SelectType.TOP:
        _select_top(distributions, selection)
    #
    return (distributions, selection)


def _make_preselection(user_selection, is_reverse):
    preselection = {}
    for item in user_selection:
        requirement = None
        requirement_ = pkg_resources.Requirement.parse(item)
        project_key = requirement_.key
        if is_reverse:
            requirement = _transform_requirement(project_key, None)
        else:
            requirement = _transform_requirement(None, requirement_)
        preselection[project_key] = requirement
    return preselection


def main(user_selection, is_reverse, is_flat):
    """ Main function """
    #
    preselection = _make_preselection(user_selection, is_reverse)
    (distributions, selection,) = _discover_distributions(
        preselection,
        is_reverse,
        is_flat,
    )
    #
    for requirement_key in sorted(selection):
        requirement = selection[requirement_key]
        if is_flat:
            if is_reverse:
                _display_reverse_flat(distributions, requirement)
            else:
                _display_forward_flat(distributions, requirement)
        else:
            if is_reverse:
                _display_reverse_tree(distributions, requirement, [])
            else:
                _display_forward_tree(distributions, requirement, [])


# EOF
