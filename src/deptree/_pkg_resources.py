#

"""Implementation based on ``pkg_resources`` from ``setuptools``."""

from __future__ import annotations

import copy
import typing

import pkg_resources

from . import _core

if typing.TYPE_CHECKING:
    import collections


def _transform_requirement(
    dependent_project_key: typing.Optional[_core.ProjectKey],
    requirement_: typing.Optional[pkg_resources.Requirement],
) -> _core.Requirement:
    #
    requirement_key = (
        typing.cast('_core.ProjectKey', requirement_.key)
        if requirement_ else None
    )
    extras = (
        typing.cast('_core.Extras', requirement_.extras)  #
        if requirement_ else ()
    )
    requirement = _core.Requirement(
        dependent_project_key=dependent_project_key,
        dependency_project_key=requirement_key,
        extras=extras,
        str_repr=str(requirement_) if requirement_ else '-',
    )
    return requirement


def _make_requirement(
    project_key: _core.ProjectKey,
    is_reverse: bool,
) -> _core.Requirement:
    #
    requirement = None
    if is_reverse:
        requirement = _transform_requirement(project_key, None)
    else:
        requirement_ = pkg_resources.Requirement.parse(project_key)
        requirement = _transform_requirement(None, requirement_)
    return requirement


def _select_flat_forward(
    distributions: _core.Distributions,
    requirement: _core.Requirement,
    selection: _core.Selection,
    chain: typing.List[_core.ProjectKey],
) -> None:
    #
    project_key = requirement.dependency_project_key
    if project_key is None:
        raise _core.InvalidForwardRequirement(requirement)
    distribution = distributions.get(project_key, None)
    #
    if project_key not in selection:
        selection[project_key] = _make_requirement(project_key, False)
    #
    if project_key not in chain:
        if distribution:
            for dependency in distribution.dependencies.values():
                _select_flat_forward(
                    distributions,
                    dependency,
                    selection,
                    chain + [project_key],
                )


def _select_flat_reverse(
    distributions: _core.Distributions,
    requirement: _core.Requirement,
    selection: _core.Selection,
    chain: typing.List[_core.ProjectKey],
) -> None:
    #
    project_key = requirement.dependent_project_key
    if project_key is None:
        raise _core.InvalidReverseRequirement(requirement)
    distribution = distributions.get(project_key, None)
    #
    if project_key not in selection:
        selection[project_key] = _make_requirement(project_key, True)
    #
    if project_key not in chain:
        if distribution:
            for dependent_key in distribution.dependents:
                dependent_distribution = distributions[dependent_key]
                dependencies = dependent_distribution.dependencies
                dependency_requirement = dependencies[project_key]
                _select_flat_reverse(
                    distributions,
                    dependency_requirement,
                    selection,
                    chain + [project_key],
                )


def _select_flat(
    distributions: _core.Distributions,
    is_reverse: bool,
    preselection: _core.Selection,
    selection: _core.Selection,
) -> None:
    #
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


def _visit_forward(
    distributions: _core.Distributions,
    requirement: _core.Requirement,
    visited: typing.List[_core.ProjectKey],
    chain: typing.List[_core.ProjectKey],
) -> None:
    #
    distribution_key = requirement.dependency_project_key
    if distribution_key is None:
        raise _core.InvalidForwardRequirement(requirement)
    if distribution_key not in visited:
        visited.append(distribution_key)
    if distribution_key not in chain:
        distribution = distributions.get(distribution_key, None)
        if distribution:
            for dependency_key in distribution.dependencies:
                dependency = distribution.dependencies[dependency_key]
                _visit_forward(
                    distributions,
                    dependency,
                    visited,
                    chain + [distribution_key],
                )


def _visit_reverse(
    distributions: _core.Distributions,
    requirement: _core.Requirement,
    visited: typing.List[_core.ProjectKey],
    chain: typing.List[_core.ProjectKey],
) -> None:
    #
    distribution_key = requirement.dependent_project_key
    if distribution_key is None:
        raise _core.InvalidReverseRequirement(requirement)
    if distribution_key not in visited:
        visited.append(distribution_key)
    if distribution_key not in chain:
        distribution = distributions.get(distribution_key, None)
        if distribution:
            for dependent_key in distribution.dependents:
                dependent_distribution = distributions[dependent_key]
                dependencies = dependent_distribution.dependencies
                dependency_requirement = dependencies[distribution_key]
                _visit_reverse(
                    distributions,
                    dependency_requirement,
                    visited,
                    chain + [distribution_key],
                )


def _find_orphan_cycles(
    distributions: _core.Distributions,
    selection: _core.Selection,
    is_reverse: bool,
) -> None:
    #
    visited: typing.List[_core.ProjectKey] = []
    for distribution_key in selection:
        if is_reverse:
            _visit_reverse(
                distributions,
                selection[distribution_key],
                visited,
                [],
            )
        else:
            _visit_forward(
                distributions,
                selection[distribution_key],
                visited,
                [],
            )
    #
    has_maybe_more_orphans = True
    max_detections = 99
    detections_counter = 0
    # pylint: disable-next=while-used
    while has_maybe_more_orphans and detections_counter < max_detections:
        detections_counter += 1
        has_maybe_more_orphans = False
        for distribution_key in distributions:
            if distribution_key not in visited:
                requirement = _make_requirement(distribution_key, is_reverse)
                selection[distribution_key] = requirement
                if is_reverse:
                    _visit_reverse(distributions, requirement, visited, [])
                else:
                    _visit_forward(distributions, requirement, visited, [])
                has_maybe_more_orphans = True
                break


def _select_bottom(
    distributions: _core.Distributions,
    selection: _core.Selection,
) -> None:
    #
    for distribution_key in distributions:
        if distribution_key not in selection:
            distribution = distributions[distribution_key]
            if not distribution.dependencies:
                selection[distribution_key] = (
                    _make_requirement(distribution_key, True)
                )
    _find_orphan_cycles(distributions, selection, True)


def _select_top(
    distributions: _core.Distributions,
    selection: _core.Selection,
) -> None:
    #
    for distribution_key in distributions:
        if distribution_key not in selection:
            distribution = distributions[distribution_key]
            if not distribution.dependents:
                selection[distribution_key] = (
                    _make_requirement(distribution_key, False)
                )
    _find_orphan_cycles(distributions, selection, False)


def _discover_distributions(  # pylint: disable=too-complex
    preselection: _core.Selection,
    is_reverse: bool,
    is_flat: bool,
) -> typing.Tuple[_core.Distributions, _core.Selection]:
    #
    distributions = typing.cast('_core.Distributions', {})
    selection = copy.deepcopy(preselection)
    #
    select_type = _core.get_select_type(
        bool(preselection),
        is_flat,
        is_reverse,
    )
    #
    for distribution_ in list(pkg_resources.working_set):
        project_key = typing.cast('_core.ProjectKey', distribution_.key)
        distribution = distributions.setdefault(
            project_key,
            _core.Distribution(),
        )
        distribution.found = True
        distribution.project_name = (
            typing.cast('_core.ProjectLabel', distribution_.project_name)
        )
        distribution.version = (
            typing.cast('_core.ProjectVersion', distribution_.version)
        )
        #
        extras = (
            preselection[project_key].extras
            if project_key in preselection else ()
        )
        #
        if (
            select_type == _core.SelectType.ALL
            and project_key not in selection
        ):
            selection[project_key] = _make_requirement(project_key, is_reverse)
        #
        for requirement_ in distribution_.requires(extras=extras):
            requirement = _transform_requirement(project_key, requirement_)
            dependency_key = requirement.dependency_project_key
            if dependency_key is None:
                raise _core.InvalidForwardRequirement(requirement)
            dependency = distributions.setdefault(
                dependency_key,
                _core.Distribution(),
            )
            dependency.dependents.append(project_key)
            distribution.dependencies[dependency_key] = requirement
            #
            try:
                pkg_resources.get_distribution(requirement_)
            except pkg_resources.VersionConflict:
                dependency.conflicts.append(project_key)
            except pkg_resources.DistributionNotFound:
                pass
            #
            if (  #
                    select_type == _core.SelectType.ALL
                    and dependency_key not in selection
            ):
                selection[dependency_key] = _make_requirement(
                    dependency_key,
                    is_reverse,
                )
    #
    if select_type == _core.SelectType.FLAT:
        _select_flat(distributions, is_reverse, preselection, selection)
    elif select_type == _core.SelectType.BOTTOM:
        _select_bottom(distributions, selection)
    elif select_type == _core.SelectType.TOP:
        _select_top(distributions, selection)
    #
    return (distributions, selection)


def _make_preselection(
    user_selection: collections.abc.Iterable[str],
    is_reverse: bool,
) -> _core.Selection:
    #
    preselection = typing.cast('_core.Selection', {})
    for item in user_selection:
        requirement = None
        requirement_ = pkg_resources.Requirement.parse(item)
        project_key = typing.cast('_core.ProjectKey', requirement_.key)
        requirement = (
            _transform_requirement(project_key, None)
            if is_reverse else _transform_requirement(None, requirement_)
        )
        preselection[project_key] = requirement
    return preselection


def build_model(
    user_selection: collections.abc.Iterable[str],
    is_reverse: bool,
    is_flat: bool,
) -> typing.Tuple[_core.Distributions, _core.Selection]:
    """CLI main function."""
    #
    preselection = _make_preselection(user_selection, is_reverse)
    (distributions, selection) = _discover_distributions(
        preselection,
        is_reverse,
        is_flat,
    )
    return (distributions, selection)


# EOF
