# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase

from q2_fragment_insertion._type import Placements, SeppReferenceDatabase


class TestTypes(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_placements_semantic_type_registration(self):
        self.assertRegisteredSemanticType(Placements)

    def test_sepp_ref_db_semantic_type_registration(self):
        self.assertRegisteredSemanticType(SeppReferenceDatabase)
