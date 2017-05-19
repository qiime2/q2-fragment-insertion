# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.plugin.testing import TestPluginBase


class TestDenoiseUtil(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def setUp(self):
        super().setUp()

        #self.table = self.get_data_path('expected/util')


if __name__ == '__main__':
    unittest.main()
