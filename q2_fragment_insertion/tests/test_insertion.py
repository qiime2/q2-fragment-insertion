# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import shutil
import unittest

import biom
import skbio
import pandas as pd
from pandas.testing import assert_frame_equal

from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_data import DNAIterator


class TestSepp(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def _cp_fp(self, frm, to):
        shutil.copy(self.get_data_path(frm),
                    os.path.join(self.temp_dir.name, to))

    def setUp(self):
        super().setUp()
        self.action = self.plugin.actions['sepp']

        input_sequences_fp = self.get_data_path('seqs-to-query.fasta')
        self.input_sequences = Artifact.import_data('FeatureData[Sequence]',
                                                    input_sequences_fp)

        self._cp_fp('ref-tree.nwk', 'tree.nwk')
        self._cp_fp('ref-seqs-aligned.fasta', 'aligned-dna-sequences.fasta')
        self._cp_fp('ref-raxml-info.txt', 'raxml-info.txt')

        self.reference_db = Artifact.import_data('SeppReferenceDatabase',
                                                 self.temp_dir.name)

    def test_exercise_sepp(self):
        obs_tree_artifact, obs_placements_artifact = self.action(
            self.input_sequences, self.reference_db,
            alignment_subset_size=1000, placement_subset_size=5000)

        tree = obs_tree_artifact.view(skbio.TreeNode)
        obs_tree = {n.name for n in tree.tips()}
        seqs = {r.metadata['id'] for r
                in self.input_sequences.view(DNAIterator)}
        self.assertTrue(seqs <= obs_tree)

        obs_placements = obs_placements_artifact.view(dict)
        self.assertEqual(set(obs_placements.keys()),
                         {'tree', 'placements', 'metadata', 'version',
                          'fields'})


class TestClassify(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def setUp(self):
        super().setUp()
        self.action = self.plugin.actions['classify_otus_experimental']

        input_sequences_fp = self.get_data_path('seqs-to-query.fasta')
        self.input_sequences = Artifact.import_data('FeatureData[Sequence]',
                                                    input_sequences_fp)

        tree_fp = self.get_data_path('sepp-results.nwk')
        self.tree = Artifact.import_data('Phylogeny[Rooted]', tree_fp)

        taxa_fp = self.get_data_path('ref-taxa.tsv')
        self.taxonomy = Artifact.import_data('FeatureData[Taxonomy]', taxa_fp)

    def test_exercise_classify_otus_experimental(self):
        obs_artifact, = self.action(self.input_sequences, self.tree,
                                    self.taxonomy)
        obs = obs_artifact.view(pd.DataFrame)

        exp_artifact = Artifact.import_data(
            'FeatureData[Taxonomy]', self.get_data_path('sepp-results.tsv'))
        exp = exp_artifact.view(pd.DataFrame)

        assert_frame_equal(obs, exp)

    def test_mismatched_tree(self):
        # Just load up the reference tree instead of creating new test data
        wrong_tree_fp = self.get_data_path('ref-tree.nwk')
        wrong_tree = Artifact.import_data('Phylogeny[Rooted]', wrong_tree_fp)
        with self.assertRaisesRegex(ValueError, 'None of.*can be found.*'):
            self.action(self.input_sequences, wrong_tree, self.taxonomy)

    def test_mismatched_taxonomy(self):
        wrong_taxa_fp = self.get_data_path('another-ref-taxa.tsv')
        wrong_taxa = Artifact.import_data('FeatureData[Taxonomy]',
                                          wrong_taxa_fp)
        with self.assertRaisesRegex(ValueError,
                                    'Not all OTUs.*1 feature.*\n.*879972'):
            self.action(self.input_sequences, self.tree, wrong_taxa)


class TestFilter(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def setUp(self):
        super().setUp()
        self.action = self.plugin.actions['filter_features']

        table_fp = self.get_data_path('table.json')
        self.table = Artifact.import_data('FeatureTable[Frequency]', table_fp,
                                          view_type='BIOMV100Format')

        tree_fp = self.get_data_path('sepp-results.nwk')
        self.tree = Artifact.import_data('Phylogeny[Rooted]', tree_fp)

    def test_exercise_filter_features(self):
        filtered_table_artifact, removed_table_artifact = self.action(
            self.table, self.tree)

        filtered_table = filtered_table_artifact.view(biom.Table)
        removed_table = removed_table_artifact.view(biom.Table)

        self.assertEqual(filtered_table.sum(), 1247)
        self.assertEqual(removed_table.sum(), 1224)

    def test_filter_features_nooverlap(self):
        # Just load up the reference tree instead of creating new test data
        wrong_tree_fp = self.get_data_path('ref-tree.nwk')
        wrong_tree = Artifact.import_data('Phylogeny[Rooted]', wrong_tree_fp)
        with self.assertRaisesRegex(ValueError,
                                    'Not a single fragment.*empty'):
            self.action(self.table, wrong_tree)


if __name__ == '__main__':
    unittest.main()
