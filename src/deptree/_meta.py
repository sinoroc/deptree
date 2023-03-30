#

"""Meta information."""

import importlib_metadata

PROJECT_NAME = 'deptree'


def _get_metadata() -> importlib_metadata.PackageMetadata:
    return importlib_metadata.metadata(PROJECT_NAME)


def get_summary() -> str:
    """Get project's summary."""
    metadata = _get_metadata()
    return metadata['Summary']


def get_version() -> str:
    """Get project's version string."""
    metadata = _get_metadata()
    return metadata['Version']


# EOF
