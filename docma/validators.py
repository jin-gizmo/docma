"""
Validators validate content during the compilation phase.

Each validator selects files based on matching a glob pattern against the
filename. The first validator wins so function ordering in this file is
critical.

"""

from __future__ import annotations

import json
from logging import getLogger
from pathlib import Path
from typing import Callable

import altair as alt
import jsonschema
import yaml

from docma.config import LOGNAME
from docma.exceptions import DocmaInternalError, DocmaPackageError
from docma.jinja import DocmaJinjaEnvironment
from docma.lib.http import get_url
from docma.lib.jsonschema import FORMAT_CHECKER
from docma.lib.query import DocmaQuerySpecification

LOG = getLogger(LOGNAME)

_validators = []

_jinja_env = DocmaJinjaEnvironment(autoescape=True)


# ------------------------------------------------------------------------------
def validator(*glob: str) -> Callable:
    """Register validators for the specified file patterns."""

    def decorate(func: Callable) -> Callable:
        """Register the handler function."""
        for pattern in glob:
            _validators.append((pattern, func))
        return func

    return decorate


# ------------------------------------------------------------------------------
@validator('config.yaml')
def _config(content: bytes):
    """Validate the template config file."""

    config = yaml.safe_load(content)
    try:
        config_schema = yaml.safe_load(
            (Path(__file__).parent / 'lib/config-schema.yaml').read_text()
        )
    except Exception as e:
        raise DocmaInternalError(f'Error reading config-schema.yaml: {e}')

    LOG.debug('Validating config against schema')
    jsonschema.validate(config, config_schema, format_checker=FORMAT_CHECKER)

    # If there is a schema for parameters provided, validate that
    params_schema = config.get('parameters', {}).get('schema')
    if params_schema:
        LOG.debug('Validating parameter schema')
        params_validator_cls = jsonschema.validators.validator_for(params_schema)
        params_validator_cls.check_schema(params_schema)

    # Transitional warning until locale becomes mandatory
    if not config.get('parameters', {}).get('defaults', {}).get('locale'):
        LOG.warning('parameters->defaults->locale should be set in config.yaml')


# ------------------------------------------------------------------------------
@validator('*.html', '*.htm', '*.md')
def _content(content: bytes):
    """
    Validate content files (HTML, Markdown etc).

    All we do here is make sure the Jinja parses ok. We don't check for valid
    HTML etc.
    """

    _jinja_env.from_string(content.decode('utf-8'))


# ------------------------------------------------------------------------------
@validator('charts/*.yaml')
def _charts(content: bytes):
    """Validate Vega-Lite chart specifications using the embedded schema reference."""

    chart_spec = yaml.safe_load(content)
    try:
        schema = chart_spec['$schema']
    except KeyError:
        raise DocmaPackageError('No $schema defined')
    schema = json.loads(get_url(schema))
    alt.Chart.validate(chart_spec, schema)


# ------------------------------------------------------------------------------
@validator('queries/*.yaml')
def _queries(content: bytes):
    """Validate query specifications."""

    DocmaQuerySpecification(name='??', **yaml.safe_load(content))


# ------------------------------------------------------------------------------
@validator('*.yaml')
def _yaml(content: bytes):
    """Validate YAML files."""

    yaml.safe_load(content)


# ------------------------------------------------------------------------------
def validate_content(path: Path, content: bytes):
    """
    Validate content during the compilation phase.

    :param path:    The path of the file to validate. This is not used to
                    obtain the contents but only to determine what validator to
                    apply.
    :param content: The actual content to be validated.
    :raise DocmaPackageError:   For invalid content.
    """

    for pattern, func in _validators:
        if path.match(pattern):
            try:
                LOG.info('Validating %s', path)
                func(content)
                LOG.debug('Validated %s', path)
            except DocmaInternalError:
                raise
            except Exception as e:
                raise DocmaPackageError(f'{path}: {e}')
            break


# ------------------------------------------------------------------------------
def validate_file(path: Path) -> None:
    """
    Validate the contents og a file during the compilation phase.

    This looks for a validator, based on filename pattern and runs the first
    one it finds. If there is no validator that matches it is assumed to be
    valid.

    :param path:        File path to validate.
    :raise DocmaPackageError:   For invalid content.
    """

    validate_content(path, path.read_bytes())
