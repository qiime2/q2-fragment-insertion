# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from setuptools import setup, find_packages


setup(
    name="q2-fragment-insertion",
    version="2018.2.0.dev0",
    packages=find_packages(),
    author="Daniel McDonald",
    author_email="wasade@gmail.com",
    description="Fragment insertion into existing phylogenies",
    entry_points={
        "qiime2.plugins":
        ["q2-fragment-insertion=q2_fragment_insertion.plugin_setup:plugin"]
    },
    license='BSD-3-Clause',
    package_data={
        'q2_fragment_insertion.tests': ['data/*']}
)
