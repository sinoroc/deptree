#

"""Implementation based on ``pkg_resources`` from ``setuptools``."""

from __future__ import annotations

import copy
import dataclasses
import enum
import typing

import pkg_resources

if typing.TYPE_CHECKING:
    import collections.abc
    #
    Extra = typing.NewType('Extra', str)
    Extras = typing.Tuple[Extra, ...]
    ProjectKey = typing.NewType('ProjectKey', str)
    ProjectLabel = typing.NewType('ProjectLabel', str)
    ProjectVersion = typing.NewType('ProjectVersion', str)
    #
    Distributions = typing.NewType(
        'Distributions',
        typing.Dict[ProjectKey, 'Distribution'],
    )
    Requirements = typing.NewType(
        'Requirements',
        typing.Dict[ProjectKey, 'Requirement'],
    )
    Selection = typing.NewType(
        'Selection',
        typing.Dict[ProjectKey, 'Requirement'],
    )

INDENTATION = 2


class DeptreeException(Exception):
    """Base exception."""


class ImpossibleCase(DeptreeException):
    """Impossible case."""


class UnknownDistributionInChain(ImpossibleCase):
    """Distribution not found although it is in chain."""


class InvalidForwardRequirement(ImpossibleCase):
    """Invalid forward requirement."""


class InvalidReverseRequirement(ImpossibleCase):
    """Invalid reverse requirement."""


@dataclasses.dataclass
class Requirement:
    """Dependency requirement."""

    dependent_project_key: typing.Optional[ProjectKey]
    dependency_project_key: typing.Optional[ProjectKey]
    extras: Extras
    str_repr: str


@dataclasses.dataclass
class Distribution:
    """Distribution of a specific project for a specific version."""

    conflicts: typing.List[ProjectKey] = (
        dataclasses.field(default_factory=list)
    )
    dependencies: Requirements = typing.cast(
        'Requirements',
        dataclasses.field(default_factory=dict),
    )
    dependents: typing.List[ProjectKey] = (
        dataclasses.field(default_factory=list)
    )
    found: bool = False
    project_name: typing.Optional[ProjectLabel] = None
    version: typing.Optional[ProjectVersion] = None


def _display_conflict(
    distribution: Distribution,
    requirement: Requirement,
    depth: int = 0,
) -> None:
    #
    print(
        f"{' ' * INDENTATION * depth}"
        f"{distribution.project_name}=={distribution.version}"
        f"  # !!! CONFLICT {requirement.str_repr}"
    )


def _display_circular(
    distribution: Distribution,
    requirement: Requirement,
    depth: int = 0,
) -> None:
    #
    print(
        f"{' ' * INDENTATION * depth}"
        f"{distribution.project_name}"
        f"  # !!! CIRCULAR {requirement.str_repr}"
    )


def _display_flat(distribution: Distribution) -> None:
    #
    print(f"{distribution.project_name}=={distribution.version}")


def _display_flat_dependency(requirement: Requirement) -> None:
    #
    print(f"# {requirement.str_repr}")


def _display_flat_dependent(
    distribution: Distribution,
    requirement: Requirement,
) -> None:
    #
    print(f"# {distribution.project_name}: {requirement.str_repr}")


def _display_good(
    distribution: Distribution,
    requirement: Requirement,
    depth: int = 0,
) -> None:
    #
    print(
        f"{' ' * INDENTATION * depth}"
        f"{distribution.project_name}=={distribution.version}"
        f"  # {requirement.str_repr}"
    )


def _display_missing(
    project_key: ProjectKey,
    requirement: Requirement,
    depth: int = 0,
) -> None:
    #
    print(
        f"{' ' * INDENTATION * depth}"
        f"{project_key}"
        f"  # !!! MISSING {requirement.str_repr}"
    )


def _display_unknown(
    project_key: ProjectKey,
    requirement: Requirement,
    depth: int = 0,
) -> None:
    #
    print(
        f"{' ' * INDENTATION * depth}"
        f"{project_key}"
        f"  # !!! UNKNOWN {requirement.str_repr}"
    )


def _display_forward_tree(
    distributions: Distributions,
    requirement: Requirement,
    chain: typing.List[ProjectKey],
) -> None:
    #
    if requirement.dependency_project_key is None:
        raise InvalidForwardRequirement(requirement)
    #
    depth = len(chain)
    project_key = requirement.dependency_project_key
    distribution = distributions.get(project_key, None)
    if project_key in chain:
        if distribution is None:
            raise UnknownDistributionInChain(requirement, project_key)
        _display_circular(distribution, requirement, depth)
    else:
        if not distribution:
            _display_unknown(project_key, requirement, depth)
        elif distribution.found is not True:
            _display_missing(project_key, requirement, depth)
        else:
            if distribution.conflicts:
                _display_conflict(distribution, requirement, depth)
            else:
                _display_good(distribution, requirement, depth)
            #
            for dependency in distribution.dependencies.values():
                _display_forward_tree(
                    distributions,
                    dependency,
                    chain + [project_key],
                )


def _display_reverse_tree(
    distributions: Distributions,
    requirement: Requirement,
    chain: typing.List[ProjectKey],
) -> None:
    #
    depth = len(chain)
    project_key = requirement.dependent_project_key
    if project_key is None:
        raise InvalidReverseRequirement(requirement)
    distribution = distributions.get(project_key, None)
    if project_key in chain:
        if distribution is None:
            raise UnknownDistributionInChain(requirement, project_key)
        _display_circular(distribution, requirement, depth)
    else:
        if not distribution:
            _display_unknown(project_key, requirement, depth)
        else:
            if distribution.found is not True:
                _display_missing(project_key, requirement, depth)
            elif distribution.conflicts:
                _display_conflict(distribution, requirement, depth)
            else:
                _display_good(distribution, requirement, depth)
            #
            for dependent_key in distribution.dependents:
                dependent_distribution = distributions[dependent_key]
                dependencies = dependent_distribution.dependencies
                dependency_requirement = dependencies[project_key]
                _display_reverse_tree(
                    distributions,
                    dependency_requirement,
                    chain + [project_key],
                )


def _display_forward_flat(
    distributions: Distributions,
    requirement: Requirement,
) -> None:
    #
    project_key = requirement.dependency_project_key
    if project_key is None:
        raise InvalidForwardRequirement(requirement)
    distribution = distributions.get(project_key, None)
    if not distribution:
        _display_unknown(project_key, requirement)
    else:
        if distribution.found is not True:
            _display_missing(project_key, requirement)
        elif distribution.conflicts:
            _display_conflict(distribution, requirement)
        else:
            _display_flat(distribution)
        #
        for dependency_requirement in distribution.dependencies.values():
            _display_flat_dependency(dependency_requirement)
    #
    print("")


def _display_reverse_flat(
    distributions: Distributions,
    requirement: Requirement,
) -> None:
    #
    project_key = requirement.dependent_project_key
    if project_key is None:
        raise InvalidReverseRequirement(requirement)
    distribution = distributions.get(project_key, None)
    if not distribution:
        _display_unknown(project_key, requirement)
    else:
        for dependent_key in distribution.dependents:
            dependent_distribution = distributions[dependent_key]
            dependencies = dependent_distribution.dependencies
            dependency_requirement = dependencies[project_key]
            _display_flat_dependent(
                distributions[dependent_key],
                dependency_requirement,
            )
        #
        if distribution.found is not True:
            _display_missing(project_key, requirement)
        elif distribution.conflicts:
            _display_conflict(distribution, requirement)
        else:
            _display_flat(distribution)
    #
    print("")


def _transform_requirement(
    dependent_project_key: typing.Optional[ProjectKey],
    requirement_: typing.Optional[pkg_resources.Requirement],
) -> Requirement:
    #
    requirement_key = (
        typing.cast('ProjectKey', requirement_.key) if requirement_ else None
    )
    extras = typing.cast('Extras', requirement_.extras) if requirement_ else ()
    requirement = Requirement(
        dependent_project_key=dependent_project_key,
        dependency_project_key=requirement_key,
        extras=extras,
        str_repr=str(requirement_) if requirement_ else '-',
    )
    return requirement


def _make_requirement(
    project_key: ProjectKey,
    is_reverse: bool,
) -> Requirement:
    #
    requirement = None
    if is_reverse:
        requirement = _transform_requirement(project_key, None)
    else:
        requirement_ = pkg_resources.Requirement.parse(project_key)
        requirement = _transform_requirement(None, requirement_)
    return requirement


def _select_flat_forward(
    distributions: Distributions,
    requirement: Requirement,
    selection: Selection,
    chain: typing.List[ProjectKey],
) -> None:
    #
    project_key = requirement.dependency_project_key
    if project_key is None:
        raise InvalidForwardRequirement(requirement)
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
    distributions: Distributions,
    requirement: Requirement,
    selection: Selection,
    chain: typing.List[ProjectKey],
) -> None:
    #
    project_key = requirement.dependent_project_key
    if project_key is None:
        raise InvalidReverseRequirement(requirement)
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
    distributions: Distributions,
    is_reverse: bool,
    preselection: Selection,
    selection: Selection,
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
    distributions: Distributions,
    requirement: Requirement,
    visited: typing.List[ProjectKey],
    chain: typing.List[ProjectKey],
) -> None:
    #
    distribution_key = requirement.dependency_project_key
    if distribution_key is None:
        raise InvalidForwardRequirement(requirement)
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
    distributions: Distributions,
    requirement: Requirement,
    visited: typing.List[ProjectKey],
    chain: typing.List[ProjectKey],
) -> None:
    #
    distribution_key = requirement.dependent_project_key
    if distribution_key is None:
        raise InvalidReverseRequirement(requirement)
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
    distributions: Distributions,
    selection: Selection,
    is_reverse: bool,
) -> None:
    #
    visited: typing.List[ProjectKey] = []
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
    distributions: Distributions,
    selection: Selection,
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
    distributions: Distributions,
    selection: Selection,
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


class _SelectType(enum.Enum):
    ALL = enum.auto()
    BOTTOM = enum.auto()
    FLAT = enum.auto()
    USER = enum.auto()
    TOP = enum.auto()


def _get_select_type(
    has_preselection: bool,
    is_flat: bool,
    is_reverse: bool,
) -> _SelectType:
    #
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


def _discover_distributions(
    preselection: Selection,
    is_reverse: bool,
    is_flat: bool,
) -> typing.Tuple[Distributions, Selection]:
    #
    distributions = typing.cast('Distributions', {})
    selection = copy.deepcopy(preselection)
    #
    select_type = _get_select_type(bool(preselection), is_flat, is_reverse)
    #
    for distribution_ in list(pkg_resources.working_set):
        project_key = typing.cast('ProjectKey', distribution_.key)
        distribution = distributions.setdefault(
            project_key,
            Distribution(),
        )
        distribution.found = True
        distribution.project_name = (
            typing.cast('ProjectLabel', distribution_.project_name)
        )
        distribution.version = (
            typing.cast('ProjectVersion', distribution_.version)
        )
        #
        extras = (
            preselection[project_key].extras
            if project_key in preselection else ()
        )
        #
        if select_type == _SelectType.ALL and project_key not in selection:
            selection[project_key] = _make_requirement(project_key, is_reverse)
        #
        for requirement_ in distribution_.requires(extras=extras):
            requirement = _transform_requirement(project_key, requirement_)
            dependency_key = requirement.dependency_project_key
            if dependency_key is None:
                raise InvalidForwardRequirement(requirement)
            dependency = distributions.setdefault(
                dependency_key,
                Distribution(),
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
                    select_type == _SelectType.ALL
                    and dependency_key not in selection
            ):
                selection[dependency_key] = _make_requirement(
                    dependency_key,
                    is_reverse,
                )
    #
    if select_type == _SelectType.FLAT:
        _select_flat(distributions, is_reverse, preselection, selection)
    elif select_type == _SelectType.BOTTOM:
        _select_bottom(distributions, selection)
    elif select_type == _SelectType.TOP:
        _select_top(distributions, selection)
    #
    return (distributions, selection)


def _make_preselection(
    user_selection: collections.abc.Iterable[str],
    is_reverse: bool,
) -> Selection:
    #
    preselection = typing.cast('Selection', {})
    for item in user_selection:
        requirement = None
        requirement_ = pkg_resources.Requirement.parse(item)
        project_key = typing.cast('ProjectKey', requirement_.key)
        if is_reverse:
            requirement = _transform_requirement(project_key, None)
        else:
            requirement = _transform_requirement(None, requirement_)
        preselection[project_key] = requirement
    return preselection


def main(
    user_selection: collections.abc.Iterable[str],
    is_reverse: bool,
    is_flat: bool,
) -> int:
    """CLI main function."""
    #
    preselection = _make_preselection(user_selection, is_reverse)
    (distributions, selection) = _discover_distributions(
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
    return 0


# EOF
