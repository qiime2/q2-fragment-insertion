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
import tarfile
import subprocess


def _initial():
    import shutil

    if shutil.which('java') is None:
        raise ValueError('java not found')

    result = subprocess.run(['java', '-version'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if 'java version' not in result.stderr.decode('ascii'):
        raise ValueError(('Please verify that java is installed and working. '
                          'As a first test, please execute "java -version" '
                          'and make sure the output shows there is an actual '
                          'version installed. OSX lies. If Java needs to be '
                          'installed, please obtain the 1.8 or greater Java '
                          'Runtime Environment (JRE) from Oracle.com. A '
                          'google search for "download jre" is likely to be '
                          'sufficient.'))


def _post(obj):
    import urllib.request
    import shutil
    import os

    src_url = ('https://raw.github.com/smirarab/sepp-refs/'
               'master/gg/sepp-package.tar.bz')

    assets_dir = os.path.join(obj.install_libbase,
                              'q2_fragment_insertion/assets/')

    if not os.path.exists(assets_dir):
        os.mkdir(assets_dir)

    out_f = 'sepp-package.tar.bz'
    with urllib.request.urlopen(src_url) as response, open(out_f, 'wb') as out:
        shutil.copyfileobj(response, out)

    opened = tarfile.open(out_f, "r:bz2")
    opened.extractall(path=assets_dir)
    opened.close()

    obj.execute(_config_sepp, [assets_dir], 'Configuring SEPP')


def _config_sepp(assets_dir):
    subprocess.run(['python', 'setup.py', 'config', '-c'], check=True,
                   cwd=assets_dir + '/sepp-package/sepp')


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        _initial()
        install.run(self)
        _post(self)


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        _initial()
        develop.run(self)
        _post(self)


setup(
    name="q2-fragment-insertion",
    version="2017.5.0.dev0",
    packages=find_packages(),
    author="Daniel McDonald",
    author_email="wasade@gmail.com",
    description="Fragment insertion into existing phylogenies",
    entry_points={
        "qiime2.plugins":
        ["q2-fragment-insertion=q2_fragment_insertion.plugin_setup:plugin"]
    },
    cmdclass={'install': PostInstallCommand,
              'develop': PostDevelopCommand},
    package_data={
        'q2_fragment_insertion.tests': ['data/*']}
)
