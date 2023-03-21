#

""" Meta information
"""

import importlib_metadata

PROJECT_NAME = 'deptree'


def _get_metadata():
    return importlib_metadata.metadata(PROJECT_NAME)


def get_summary():
    """Get project's summary."""
    metadata = _get_metadata()
    return metadata['Summary']


def get_version():
    """Get project's version string."""
    metadata = _get_metadata()
    return metadata['Version']


# EOF
