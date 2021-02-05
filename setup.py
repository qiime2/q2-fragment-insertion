# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages
import versioneer


setup(
    name="q2-fragment-insertion",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Stefan Janssen",
    author_email="stefan.m.janssen@gmail.com",
    description="Fragment insertion into existing phylogenies",
    entry_points={
        "qiime2.plugins":
        ["q2-fragment-insertion=q2_fragment_insertion.plugin_setup:plugin"]
    },
    url="https://qiime2.org",
    license='BSD-3-Clause',
    package_data={
        'q2_fragment_insertion': ['citations.bib'],
        'q2_fragment_insertion.tests': ['data/*']
    },
    zip_safe=False,
)
