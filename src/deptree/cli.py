#

"""Command line interface."""

import argparse
import typing

from . import _core
from . import _i18n
from . import _meta
from . import _pkg_resources

_ = _i18n._


def _build_args_parser() -> argparse.ArgumentParser:
    args_parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=_meta.get_summary(),
    )
    args_parser.add_argument(
        '--version',
        action='version',
        version=_meta.get_version(),
    )
    args_parser.add_argument(
        '-r',
        '--reverse',
        action='store_true',
        help=_("show dependent projects instead of dependencies"),
    )
    args_parser.add_argument(
        '-f',
        '--flat',
        action='store_true',
        help=_("show flat list instead of tree"),
    )
    args_parser.add_argument(
        'selected_projects',
        help=_("name of project whose dependencies (or dependents) to show"),
        metavar='project',
        nargs='*',
    )
    return args_parser


def _parse_args() -> typing.Tuple[typing.List[str], bool, bool]:
    #
    args_parser = _build_args_parser()
    args = args_parser.parse_args()
    user_selection: typing.List[str] = args.selected_projects
    is_reverse: bool = args.reverse
    is_flat: bool = args.reverse
    #
    return (user_selection, is_reverse, is_flat)


def main() -> int:
    """CLI main function."""
    #
    (user_selection, is_reverse, is_flat) = _parse_args()
    #
    (distributions, selection) = _pkg_resources.build_model(
        user_selection,
        is_reverse,
        is_flat,
    )
    #
    for requirement_key in sorted(selection):
        requirement = selection[requirement_key]
        if is_flat:
            if is_reverse:
                _core.display_reverse_flat(distributions, requirement)
            else:
                _core.display_forward_flat(distributions, requirement)
        elif is_reverse:
            _core.display_reverse_tree(distributions, requirement, [])
        else:
            _core.display_forward_tree(distributions, requirement, [])
    #
    return 0


# EOF
