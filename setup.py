# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def _initial():
    import os
    import shutil
    import subprocess

    path = os.getcwd()
    if shutil.which('java') is None:
        raise ValueError('java not found')

    result = subprocess.run(['java', '-version'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if 'Java(TM) SE Runtime Environment' not in result.stderr.encode('ascii'):
        raise ValueError(('Please verify that java is installed and working. '
                          'As a first test, please execute "java -version" '
                          'and make sure the output shows there is an actual '
                          'version installed. OSX lies. If Java needs to be '
                          'installed, please obtain the 1.8 or greater Java '
                          'Runtime Environment (JRE) from Oracle.com. A '
                          'google search for "download jre" is likely to be '
                          'sufficient.'))


def _post():
    import urllib.request
    import shutil

    with urllib.request.urlopen('') as response, open(out, 'wb') as out:
        shutil.copyfileobj(response, out)

    # unpack the download

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        _initial()
        install.run(self)
        _post()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        _initial()
        develop.run(self)
        _post()


setup(
    name="q2-fragment-insertion",
    version="2017.2.0.dev0",
    packages=find_packages(),
    install_requires=['qiime2 == 2017.2.*', 'pandas', 'q2-types == 2017.2.*',
                      'q2templates == 2017.2.*'],
    author="Daniel McDonald",
    author_email="wasade@gmail.com",
    description="Fragment insertion into existing phylogenies",
    entry_points={
        "qiime2.plugins":
        ["q2-fragment-insertion=q2_fragment_insertion.plugin_setup:plugin"]
    }
)
