#


""" Meta information
"""


import importlib_metadata


PROJECT_NAME = 'deptree'

_DISTRIBUTION_METADATA = importlib_metadata.metadata(PROJECT_NAME)

SUMMARY = _DISTRIBUTION_METADATA['Summary']
VERSION = _DISTRIBUTION_METADATA['Version']


# EOF
