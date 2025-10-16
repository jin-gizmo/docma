"""setup.py for docma."""

from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

__version__ = (Path(__file__).parent / 'docma' / 'VERSION').read_text().strip()

REPO_URL = 'https://github.com/jin-gizmo/docma'
REQUIRES_PYTHON = '>=3.11.0'


# ------------------------------------------------------------------------------
def find_cli_entry_points(*cli_pkg: str, entry_point: str = 'main') -> list[str]:
    """Find CLI entry point scripts in the specified CLI packages."""

    entry_points = []
    for pkg in cli_pkg:
        pkg_path = Path(pkg.replace('.', '/'))
        if not pkg_path.is_dir():
            continue
        entry_points.extend(
            [
                f'{f.stem.replace("_", "-")}={pkg}.{f.stem}:{entry_point}'
                for f in pkg_path.glob('*.py')
                if not f.name.startswith('_')
            ]
        )
    return entry_points


# ------------------------------------------------------------------------------
# Import PYPI.md and use it as the long-description. Must be in MANIFEST.in
with open('PYPI.md') as fp:
    long_description = '\n' + fp.read()

# ------------------------------------------------------------------------------
# Get pre-requisites from requirements.txt. Must be in MANIFEST.in
with open('requirements.txt') as fp:
    required = [s.strip() for s in fp.readlines()]

# Optional extras
extras = {'all': []}
for x in ('duckdb', 'lava'):
    with open(f'requirements-{x}.txt') as fp:
        extras[x] = [s.strip() for s in fp.readlines()]
        extras['all'].extend(extras[x])

# ------------------------------------------------------------------------------
packages = find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*'])
setup(
    name='docma',
    version=__version__,
    packages=packages,
    entry_points={
        'console_scripts': find_cli_entry_points(*(p for p in packages if p.endswith('.cli')))
    },
    url=REPO_URL,
    license='BSD-3-Clause',
    author='Murray Andrews',
    description='Document manufacturer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms=['macOS', 'Linux'],
    python_requires=REQUIRES_PYTHON,
    install_requires=required,
    extras_require=extras,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Documentation',
        'Topic :: Text Processing',
    ],
)
