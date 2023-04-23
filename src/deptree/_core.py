#

"""Core bits."""

from __future__ import annotations

import dataclasses
import enum
import typing

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


class SelectType(enum.Enum):
    """Selection type."""

    ALL = enum.auto()
    BOTTOM = enum.auto()
    FLAT = enum.auto()
    USER = enum.auto()
    TOP = enum.auto()


def get_select_type(
    has_preselection: bool,
    is_flat: bool,
    is_reverse: bool,
) -> SelectType:
    """Get selection type."""
    selections = {
        (False, False, False): SelectType.TOP,
        (False, False, True): SelectType.BOTTOM,
        (False, True, False): SelectType.ALL,
        (False, True, True): SelectType.ALL,
        (True, False, False): SelectType.USER,
        (True, False, True): SelectType.USER,
        (True, True, False): SelectType.FLAT,
        (True, True, True): SelectType.FLAT,
    }
    select_type = selections[(has_preselection, is_flat, is_reverse)]
    return select_type


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


def display_forward_tree(
    distributions: Distributions,
    requirement: Requirement,
    chain: typing.List[ProjectKey],
) -> None:
    """Display as tree with normal (forward) dependencies."""
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
    elif not distribution:
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
            display_forward_tree(
                distributions,
                dependency,
                chain + [project_key],
            )


def display_reverse_tree(
    distributions: Distributions,
    requirement: Requirement,
    chain: typing.List[ProjectKey],
) -> None:
    """Display as tree with reverse dependencies."""
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
    elif not distribution:
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
            display_reverse_tree(
                distributions,
                dependency_requirement,
                chain + [project_key],
            )


def display_forward_flat(
    distributions: Distributions,
    requirement: Requirement,
) -> None:
    """Display as flat list with normal (forward) dependencies."""
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


def display_reverse_flat(
    distributions: Distributions,
    requirement: Requirement,
) -> None:
    """Display as flat list with reverse dependencies."""
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


# EOF
