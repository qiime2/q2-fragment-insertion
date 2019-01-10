# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pkg_resources

from ._insertion import (sepp, classify_paths, classify_otus_experimental,
                         filter_features)
from ._version import get_versions


__version__ = get_versions()['version']
del get_versions

__all__ = ['sepp', 'classify_paths', 'classify_otus_experimental',
           'filter_features']
