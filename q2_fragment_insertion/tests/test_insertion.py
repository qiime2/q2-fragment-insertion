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
from q2_fragment_insertion._insertion import sepp_16s_greengenes
import skbio
from q2_types.feature_data import (AlignedDNASequencesDirectoryFormat,
                                   DNASequencesDirectoryFormat,
                                   DNAIterator)
from q2_types.tree import NewickFormat


class TestFragmentInsertion(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_exercise_sepp_16s_greengenes(self):
        ar = Artifact.load(self.get_data_path('real_data.qza'))
        view = ar.view(DNASequencesDirectoryFormat)

        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        obs_tree, obs_placements = sepp_16s_greengenes(
            view,
            reference_alignment=ref_aln_small,
            reference_phylogeny=ref_phylo_small)

        tree = skbio.TreeNode.read(str(obs_tree))
        obs = {n.name for n in tree.tips()}
        seqs = {r.metadata['id'] for r in ar.view(DNAIterator)}
        for seq in seqs:
            self.assertIn(seq, obs)

    def test_refmismatch(self):
        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        with self.assertRaises(ValueError):
            obs_tree, obs_placements = sepp_16s_greengenes(
                None, reference_phylogeny=ref_phylo_small)

        with self.assertRaises(ValueError):
            obs_tree, obs_placements = sepp_16s_greengenes(
                None, reference_alignment=ref_aln_small)


if __name__ == '__main__':
    unittest.main()
