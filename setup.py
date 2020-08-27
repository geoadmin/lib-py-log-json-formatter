#!/usr/bin/env python

from setuptools import setup, find_packages

PACKAGE_NAME = 'logging_utilities'

# Get description from README.md
LONG_DESCRIPTION = ''
with open('README.md', encoding='utf-8') as rd:
    LONG_DESCRIPTION = rd.read()

VERSION_LINE = list(filter(lambda l: l.startswith('VERSION'),
                           open(PACKAGE_NAME + '/__init__.py')))[0]


def get_version(version_line):
    # pylint: disable=eval-used
    version_tuple = eval(version_line.split('=')[-1])
    return ".".join(map(str, version_tuple))


setup(
    name='logging-utilities',
    version=get_version(VERSION_LINE),
    description=('Python logging utilities'),
    LONG_DESCRIPTION=LONG_DESCRIPTION,
    LONG_DESCRIPTION_content_type="text/markdown",
    platforms=["all"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License'
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
        'Topic :: System :: Logging'
    ],
    python_requires='>=3.0',
    author='ltshb',
    author_email='brice.schaffner@swisstopo.ch',
    url='https://github.com/geoadmin/lib-py-logging-utilities',
    license='BSD 3-Clause License',
    packages=find_packages()
)
