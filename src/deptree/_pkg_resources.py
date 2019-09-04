#!/usr/bin/env python3


""" deptree TODO
"""


import pkg_resources


__version__ = '0.0.0'


def _display_req(req, distributions, depth, seen):
    if 'dist' in distributions[req.key]:
        print(
            '.' * depth * 4,
            req.project_name,
            distributions[req.key]['dist'].version,
            req.specs,
            req.marker,
        )
        dist = distributions[req.key]['dist']
        _display_requirements(dist, distributions, depth + 1, seen)
    else:
        print(
            '.' * depth * 4,
            req.project_name,
            'NOT INSTALLED!',
            req.specs,
            req.marker,
        )


def _display_requirements(dist, distributions, depth, seen):
    for req in dist.requires():
        if req.key in seen:
            print("CYCLIC", seen, req.key)
        else:
            _display_req(req, distributions, depth, seen + [req.key])


def _display_dist(dist_dict, distributions):
    dist = dist_dict['dist']
    seen = [dist.key]
    print(dist.project_name, dist.version)
    _display_requirements(dist, distributions, 1, seen)


def _display(distributions):
    for dist_dict in distributions.values():
        if not dist_dict.get('is_requirement', False):
            _display_dist(dist_dict, distributions)


def main():
    """ Main function """
    distributions = {}
    working_set = pkg_resources.working_set
    for dist in working_set:  # pylint: disable=not-an-iterable
        dist_dict = distributions.setdefault(dist.key, {})
        dist_dict['dist'] = dist
        for req in dist.requires():
            req_dict = distributions.setdefault(req.key, {})
            req_dict['is_requirement'] = True
    _display(distributions)


# EOF
