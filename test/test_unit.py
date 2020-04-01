""" Unit tests
"""


import unittest

import deptree


class TestProjectVersion(unittest.TestCase):
    """ Project version string
    """

    def test_project_has_version_string(self):
        """ Project should have a vesion string
        """
        try:
            deptree.__version__
        except AttributeError as version_exception:
            self.fail(version_exception)


class TestSelectType(unittest.TestCase):
    """Selection type"""

    def setUp(self):
        self.get_select_type = (
            # pylint: disable=protected-access
            deptree._pkg_resources._get_select_type
        )
        self.select_type = (
            # pylint: disable=protected-access
            deptree._pkg_resources._SelectType
        )

    def test_select_type_all(self):
        """Selection type should be 'ALL'"""
        self.assertEqual(
            self.get_select_type(
                has_preselection=False,
                is_flat=True,
                is_reverse=False,
            ),
            self.select_type.ALL,
        )
        self.assertEqual(
            self.get_select_type(
                has_preselection=False,
                is_flat=True,
                is_reverse=True,
            ),
            self.select_type.ALL,
        )

    def test_select_type_bottom(self):
        """Selection type should be 'BOTTOM'"""
        self.assertEqual(
            self.get_select_type(
                has_preselection=False,
                is_flat=False,
                is_reverse=True,
            ),
            self.select_type.BOTTOM,
        )

    def test_select_type_flatten(self):
        """Selection type should be 'FLAT'"""
        self.assertEqual(
            self.get_select_type(
                has_preselection=True,
                is_flat=True,
                is_reverse=False,
            ),
            self.select_type.FLAT,
        )
        self.assertEqual(
            self.get_select_type(
                has_preselection=True,
                is_flat=True,
                is_reverse=True,
            ),
            self.select_type.FLAT,
        )

    def test_select_type_user(self):
        """Selection type should be 'USER'"""
        self.assertEqual(
            self.get_select_type(
                has_preselection=True,
                is_flat=False,
                is_reverse=False,
            ),
            self.select_type.USER,
        )
        self.assertEqual(
            self.get_select_type(
                has_preselection=True,
                is_flat=False,
                is_reverse=True,
            ),
            self.select_type.USER,
        )

    def test_select_type_top(self):
        """Selection type should be 'TOP'"""
        self.assertEqual(
            self.get_select_type(
                has_preselection=False,
                is_flat=False,
                is_reverse=False,
            ),
            self.select_type.TOP,
        )


# EOF
