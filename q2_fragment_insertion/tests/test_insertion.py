# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase
from q2_types.feature_data import DNAFASTAFormat, DNAIterator
from q2_fragment_insertion._insertion import sepp_16s_greengenes
import skbio


class TestDenoiseUtil(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_exercise_sepp_16s_greengenes(self):
        ar = Artifact.load(self.get_data_path('real_data.qza'))
        view = ar.view(DNAFASTAFormat)
        obs_tree, obs_placements = sepp_16s_greengenes(view)

        tree = skbio.TreeNode.read(str(obs_tree))
        obs = {n.name for n in tree.tips()}
        seqs = {r.id for r in ar.view(DNAIterator)}
        self.assertIn(seqs, obs)


if __name__ == '__main__':
    unittest.main()
