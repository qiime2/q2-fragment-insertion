# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from ._insertion import (sepp, classify_paths, classify_otus_experimental,
                         filter_features)


try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = '0.0.0+notfound'

__all__ = ['sepp', 'classify_paths', 'classify_otus_experimental',
           'filter_features']
