# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase
from io import StringIO
from contextlib import redirect_stderr
from q2_fragment_insertion._insertion import (sepp, classify_otus_experimental,
                                              filter_features)
import skbio
import pandas as pd
from pandas.testing import assert_frame_equal
from q2_types.feature_data import (AlignedDNASequencesDirectoryFormat,
                                   DNASequencesDirectoryFormat,
                                   DNAIterator)
from q2_types.tree import NewickFormat
import biom


class TestSepp(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_exercise_sepp(self):
        ar = Artifact.load(self.get_data_path('real_data.qza'))
        view = ar.view(DNASequencesDirectoryFormat)

        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        obs_tree, obs_placements = sepp(
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
            sepp(None, reference_phylogeny=ref_phylo_small)

        with self.assertRaises(ValueError):
            sepp(None, reference_alignment=ref_aln_small)

        ar_refphylo_tiny = Artifact.load(self.get_data_path(
            'reference_phylogeny_tiny.qza'))
        ref_phylo_tiny = ar_refphylo_tiny.view(NewickFormat)

        with self.assertRaises(ValueError):
            sepp(None, reference_alignment=ref_aln_small,
                 reference_phylogeny=ref_phylo_tiny)


class TestClassify(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    # def test_classify_paths(self):
    #     ar_tree = Artifact.load(self.get_data_path('sepp_tree_tiny.qza'))
    #     ar_repseq = Artifact.load(self.get_data_path('real_data.qza'))
    #
    #     obs_classification = classify_paths(
    #         ar_repseq.view(DNASequencesDirectoryFormat),
    #         ar_tree.view(NewickFormat))
    #     exp_classification = pd.read_csv(self.get_data_path(
    #         'taxonomy_real_data_tiny_paths.tsv'),
    #         index_col=0, sep="\t").fillna("")
    #     assert_frame_equal(obs_classification, exp_classification)
    #
    #     ar_tree_small = Artifact.load(
    #         self.get_data_path('sepp_tree_small.qza'))
    #     obs_classification_small = classify_paths(
    #         ar_repseq.view(DNASequencesDirectoryFormat),
    #         ar_tree_small.view(NewickFormat))
    #     exp_classification_small = pd.read_csv(self.get_data_path(
    #         'taxonomy_real_data_small_paths.tsv'),
    #         index_col=0, sep="\t").fillna("")
    #     assert_frame_equal(obs_classification_small,
    #                        exp_classification_small)
    #
    #     ar_refphylo_tiny = Artifact.load(self.get_data_path(
    #         'reference_phylogeny_tiny.qza'))
    #     ref_phylo_tiny = ar_refphylo_tiny.view(NewickFormat)
    #     with self.assertRaises(ValueError):
    #         classify_paths(
    #             ar_repseq.view(DNASequencesDirectoryFormat), ref_phylo_tiny)

    def test_classify_otus_experimental(self):
        ar_tree = Artifact.load(self.get_data_path('sepp_tree_tiny.qza'))
        ar_repseq = Artifact.load(self.get_data_path('real_data.qza'))

        obs_classification = classify_otus_experimental(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree.view(NewickFormat))
        exp_classification = pd.read_csv(self.get_data_path(
            'taxonomy_real_data_tiny_otus.tsv'),
            index_col=0, sep="\t").fillna("")
        assert_frame_equal(obs_classification, exp_classification)

        ar_tree_small = Artifact.load(
            self.get_data_path('sepp_tree_small.qza'))
        obs_classification_small = classify_otus_experimental(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree_small.view(NewickFormat))

        exp_classification_small = pd.read_csv(self.get_data_path(
            'taxonomy_real_data_small_otus.tsv'),
            index_col=0, sep="\t").fillna("")
        assert_frame_equal(obs_classification_small, exp_classification_small)

        ar_refphylo_tiny = Artifact.load(self.get_data_path(
            'reference_phylogeny_tiny.qza'))
        ref_phylo_tiny = ar_refphylo_tiny.view(NewickFormat)
        with self.assertRaises(ValueError):
            classify_otus_experimental(
                ar_repseq.view(DNASequencesDirectoryFormat), ref_phylo_tiny)

        # test that missing taxon mappings result in an error
        ar_taxonomy = Artifact.load(
            self.get_data_path('taxonomy_missingotus.qza'))

        # capture stderr message and check if its content is as expected
        captured_stderr = StringIO()
        with redirect_stderr(captured_stderr):
            with self.assertRaises(ValueError):
                classify_otus_experimental(
                    ar_repseq.view(DNASequencesDirectoryFormat),
                    ar_tree.view(NewickFormat),
                    reference_taxonomy=ar_taxonomy.view(pd.DataFrame))
        self.assertIn('The taxonomy artifact you provided does not cont',
                      captured_stderr.getvalue())
        self.assertIn('539572',
                      captured_stderr.getvalue())


class TestFilter(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_filter_features(self):
        ar_tree = Artifact.load(self.get_data_path('tree_reject.qza'))
        ar_table = Artifact.load(self.get_data_path('counts_reject.biom.qza'))

        tbl_positive, tbl_negative = filter_features(
            table=ar_table.view(biom.Table),
            tree=ar_tree.view(NewickFormat)
        )
        self.assertEqual(tbl_positive.sum(), 715)
        self.assertEqual(tbl_negative.sum(), 133)

        exp_sample_ids = set(['sample_a', 'sample_b', 'sample_c', 'sample_d'])
        self.assertEqual(set(tbl_positive.ids()) ^ exp_sample_ids, set())
        self.assertEqual(set(tbl_negative.ids()) ^ exp_sample_ids, set())

        exp_pos_feature_ids = set([
            'testseqa', 'testseqb', 'testseqc', 'testseqd', 'testseqe',
            'testseqf', 'testseqg', 'testseqh', 'testseqi', 'testseqj'])
        self.assertEqual(set(tbl_positive.ids(
            axis='observation')) ^ exp_pos_feature_ids, set())
        exp_neg_feature_ids = set(['testseq_reject_1', 'testseq_reject_2'])
        self.assertEqual(set(tbl_negative.ids(
            axis='observation')) ^ exp_neg_feature_ids, set())

    def test_filter_features_nooverlap(self):
        ar_tree = Artifact.load(self.get_data_path('tree_reject.qza'))
        ar_table = Artifact.load(self.get_data_path(
            'counts_nooverlap.biom.qza'))

        with self.assertRaises(ValueError):
            tbl_positive, tbl_negative = filter_features(
                table=ar_table.view(biom.Table),
                tree=ar_tree.view(NewickFormat)
            )


if __name__ == '__main__':
    unittest.main()
