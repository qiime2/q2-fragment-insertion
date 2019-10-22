# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_fragment_insertion._format import PlacementsFormat

from qiime2.plugin.testing import TestPluginBase


class TestFormats(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_placements_format_validate_positive(self):
        filepath = self.get_data_path('placements.json')
        fmt = PlacementsFormat(filepath, mode='r')

        fmt.validate()
        self.assertTrue(True)
