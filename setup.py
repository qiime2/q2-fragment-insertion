    err_content = result.stderr.decode('ascii')
    if ('java version' not in err_content) and \
       ('jdk version' not in err_content):
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
    err_content = result.stderr.decode('ascii')
    if ('java version' not in err_content) and \
       ('jdk version' not in err_content):
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

    # using a tagged version from Siavash's repo
    git_tag = '4.3.4'
    src_url = ('https://github.com/smirarab/sepp-refs/archive/%s.tar.gz' %
               git_tag)

    assets_dir = os.path.join(obj.install_libbase,
                              'q2_fragment_insertion/assets/')

    if not os.path.exists(assets_dir):
        os.mkdir(assets_dir)

    out_f = 'tagged-sepp-package.tar.gz'
    # 1/3: download git tagged version sources ...
    with urllib.request.urlopen(src_url) as response, open(out_f, 'wb') as out:
        shutil.copyfileobj(response, out)

    # 2/3: ... which come as one tar archive that needs to be extracted ...
    opened = tarfile.open(out_f, "r:gz")
    opened.extractall(path=obj.install_libbase)
    opened.close()

    # 3/3: ... and contains another tar archive which is extracted here.
    opened = tarfile.open(os.path.join(obj.install_libbase,
                                       'sepp-refs-%s' % git_tag,
                                       'gg', 'sepp-package.tar.bz'), "r:bz2")
    opened.extractall(path=assets_dir)
    opened.close()

    # copy patch file
    name_patch = 'passreference.patch'
    shutil.copy(name_patch, assets_dir)

    obj.execute(_patch_sepp, [assets_dir, name_patch], 'Patch run-sepp.sh')
    obj.execute(_config_sepp, [assets_dir], 'Configuring SEPP')


def _patch_sepp(assets_dir, name_patch):
    subprocess.run(['patch', 'sepp-package/run-sepp.sh', name_patch],
                   check=True, cwd=assets_dir)


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
    license='BSD-3-Clause',
    package_data={
        'q2_fragment_insertion.tests': ['data/*']}
)
