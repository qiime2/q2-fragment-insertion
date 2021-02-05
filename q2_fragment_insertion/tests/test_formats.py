# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil

from q2_fragment_insertion._format import (
    PlacementsFormat, SeppReferenceDirFmt, RAxMLinfoFormat)

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestPlacementFormat(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_validate_positive(self):
        filepath = self.get_data_path('placements.json')
        fmt = PlacementsFormat(filepath, mode='r')

        fmt.validate()
        self.assertTrue(True)

    def test_validate_negative_array(self):
        filepath = self.get_data_path('root-array.json')
        fmt = PlacementsFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'JSON object'):
            fmt.validate()

    def test_validate_negative_missing_keys(self):
        filepath = self.get_data_path('placements-missing.json')
        fmt = PlacementsFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'found.*placements.*tree'):
            fmt.validate()


class TestSeppReferenceDirFmt(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def _cp_fp(self, frm, to):
        shutil.copy(self.get_data_path(frm),
                    os.path.join(self.temp_dir.name, to))

    def test_validate_positive(self):
        self._cp_fp('ref-tree.nwk', 'tree.nwk')
        self._cp_fp('ref-seqs-aligned.fasta', 'aligned-dna-sequences.fasta')
        self._cp_fp('ref-raxml-info.txt', 'raxml-info.txt')

        fmt = SeppReferenceDirFmt(self.temp_dir.name, mode='r')

        fmt.validate()
        self.assertTrue(True)

    def test_validate_negative_missing_seqs(self):
        self._cp_fp('ref-tree.nwk', 'tree.nwk')
        self._cp_fp('seqs-to-query.fasta', 'aligned-dna-sequences.fasta')
        self._cp_fp('ref-raxml-info.txt', 'raxml-info.txt')

        fmt = SeppReferenceDirFmt(self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'missing in the phylogeny.*testseqa'):
            fmt.validate()

    def test_validate_negative_missing_tips(self):
        self._cp_fp('another-ref-tree.nwk', 'tree.nwk')
        self._cp_fp('ref-seqs-aligned.fasta', 'aligned-dna-sequences.fasta')
        self._cp_fp('ref-raxml-info.txt', 'raxml-info.txt')

        fmt = SeppReferenceDirFmt(self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'missing in the alignment.*b.*c'):
            fmt.validate()


class TestRAxMLinfoFormat(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def test_validate_positive(self):
        filepath = self.get_data_path('ref-raxml-info.txt')
        fmt = RAxMLinfoFormat(filepath, mode='r')

        fmt.validate()
        self.assertTrue(True)

    def test_validate_negative_array(self):
        filepath = self.get_data_path('root-array.json')
        fmt = RAxMLinfoFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'Missing.*RAxML'):
            fmt.validate()
