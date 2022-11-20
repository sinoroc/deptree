#

""" Meta information
"""

import importlib.metadata

PROJECT_NAME = 'deptree'


def _get_metadata():
    return importlib.metadata.metadata(PROJECT_NAME)


def get_summary():
    """Get project's summary."""
    metadata = _get_metadata()
    return metadata['Summary']


def get_version():
    """Get project's version string."""
    metadata = _get_metadata()
    return metadata['Version']


# EOF
