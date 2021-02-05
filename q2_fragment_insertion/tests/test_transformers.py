# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pathlib

from q2_fragment_insertion._format import PlacementsFormat

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestTransformers(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_dict_to_placements_format(self):
        transformer = self.get_transformer(dict, PlacementsFormat)

        obs = transformer({'foo': 1})

        with self.assertRaisesRegex(ValidationError, r'found \[\'foo\'\]'):
            # A bit of a cop-out, but this means we were able to parse the
            # JSON document.
            obs.validate(level='max')

    def test_placements_format_to_dict(self):
        transformer = self.get_transformer(PlacementsFormat, dict)

        fp = pathlib.Path(self.temp_dir.name) / pathlib.Path('placements.json')
        fp.write_text('{"foo": 1}')

        input_ = PlacementsFormat(str(fp), mode='r')
        with self.assertRaisesRegex(ValidationError, r'found \[\'foo\'\]'):
            # A bit of a cop-out, but this means we were able to parse the
            # JSON document.
            input_.validate(level='max')

        obs = transformer(input_)
        self.assertEqual(obs, {'foo': 1})
