"""Validation checker for docma new."""

import json
import sys

from docma.plugins.format_checkers.utility import is_locale, is_semantic_version

# The tojson hack is a crude form of escaping.
required_vars = {
    'template_id': '{{ cookiecutter.template_id | tojson }}',
    'template_src_dir': '{{ cookiecutter.template_src_dir | tojson }}',
    'description': '{{ cookiecutter.description | tojson }}',
    'owner': '{{ cookiecutter.owner | tojson }}',
    'version': '{{ cookiecutter.version | tojson }}',
    'locale': '{{ cookiecutter.locale | tojson }}',
}

# Decode the JSON
required_vars = {k: json.loads(v) for k, v in required_vars.items()}

errors = []
for k, v in required_vars.items():
    if not v:
        errors.append(f'ERROR: {k} must be specified')

# Field specific validations

if not is_locale(required_vars['locale']):
    errors.append(f'ERROR: {required_vars["locale"]} is not a valid locale')

if not is_semantic_version(required_vars['version']):
    errors.append(f'ERROR: {required_vars["version"]} is not a valid semantic version')

if errors:
    print('\n'.join(errors))
    sys.exit(1)

sys.exit(0)
