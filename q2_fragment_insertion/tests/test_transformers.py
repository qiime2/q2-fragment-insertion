# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pathlib

from q2_fragment_insertion._format import PlacementsFormat

from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_dict_to_placements_format(self):
        transformer = self.get_transformer(dict, PlacementsFormat)

        obs = transformer({'foo': 1})

        obs.validate(level='max')
        self.assertTrue(True)

    def test_placements_format_to_dict(self):
        transformer = self.get_transformer(PlacementsFormat, dict)

        fp = pathlib.Path(self.temp_dir.name) / pathlib.Path('placements.json')
        fp.write_text('{"foo": 1}')

        input_ = PlacementsFormat(str(fp), mode='r')
        input_.validate()

        obs = transformer(input_)
        self.assertEqual(obs, {'foo': 1})
