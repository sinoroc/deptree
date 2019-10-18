#


""" Implementation based on 'pkg_resources' from 'setuptools'
"""


import pkg_resources


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


def _display_selected(distributions, selected_projects):
    for project in selected_projects:
        project_key = project['key']
        if project_key in distributions:
            _display_dist(distributions[project_key], distributions)


def _display_all(distributions):
    for dist_dict in distributions.values():
        if not dist_dict.get('is_requirement', False):
            _display_dist(dist_dict, distributions)


def _parse_user_selection(user_selection):
    selected_projects = []
    for project in user_selection:
        requirement = pkg_resources.Requirement.parse(project)
        project = {
            'name': requirement.project_name,
            'key': requirement.key,
            'extras': requirement.extras,
        }
        selected_projects.append(project)
    return selected_projects


def _list_distributions():
    distributions = {}
    working_set = pkg_resources.working_set
    for distribution in working_set:  # pylint: disable=not-an-iterable
        distribution_dict = distributions.setdefault(distribution.key, {})
        distribution_dict['dist'] = distribution
        for requirement in distribution.requires():
            requirement_dict = distributions.setdefault(requirement.key, {})
            requirement_dict['is_requirement'] = True
    return distributions


def main(user_selection):
    """ Main function """
    distributions = _list_distributions()
    if user_selection:
        selected_projects = _parse_user_selection(user_selection)
        _display_selected(distributions, selected_projects)
    else:
        _display_all(distributions)


# EOF
