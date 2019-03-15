# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from os import environ, remove, chmod
from os.path import exists, isdir, join
from shutil import rmtree
from tempfile import mkdtemp
from qiime2.sdk import Artifact
from qiime2.plugin.testing import TestPluginBase
from q2_fragment_insertion._format import RAxMLinfoDirFmt
from q2_fragment_insertion._insertion import sepp
from q2_types.feature_data import (AlignedDNASequencesDirectoryFormat,
                                   DNASequencesDirectoryFormat)
from q2_types.tree import NewickFormat
from subprocess import CalledProcessError


class TestSepp(TestPluginBase):
    package = 'q2_fragment_insertion.tests'

    def setUp(self):
        # saving current value of PATH
        self.oldpath = environ['PATH']
        self._clean_up_files = []

    def tearDown(self):
        # restore eventually changed PATH env var
        environ['PATH'] = self.oldpath
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def test_alternative_reference(self):
        ar = Artifact.load(self.get_data_path('real_data.qza'))
        view = ar.view(DNASequencesDirectoryFormat)

        ar_refphylo = Artifact.load(self.get_data_path(
            'reference_phylogeny_small.qza'))
        ref_phylo_small = ar_refphylo.view(NewickFormat)

        ar_refaln = Artifact.load(self.get_data_path(
            'reference_alignment_small.qza'))
        ref_aln_small = ar_refaln.view(AlignedDNASequencesDirectoryFormat)

        ar_refinfo = Artifact.load(self.get_data_path(
            'silva12.8.raxmlinfo.qza'))
        ref_info = ar_refinfo.view(RAxMLinfoDirFmt)

        out_dir = mkdtemp()
        self._clean_up_files.append(out_dir)
        # create a fake run-sepp.sh binary.
        # Basically, I want to test here if the right filepaths are passed to
        # run-sepp.sh when requesting silva instead of the default reference.
        # Unfortunately, a real computation would take too long for Travis.
        # Thus, I replace the actual binary script here with something that
        # takes the parameters and echos them to stderr and fails. This way,
        # we can expect to find file paths in the msg error message.
        fp_fake_sepp = join(out_dir, 'run-sepp.sh')
        with open(fp_fake_sepp, 'w') as f:
            f.write('#!/bin/bash\n\n'
                    'while [[ $# -gt 0 ]]\n'
                    'do\n'
                    '	key="$1"\n'
                    '	case $key in\n'
                    '		-a)\n'
                    '			a="$2"\n'
                    '			shift # past argument\n'
                    '			;;\n'
                    '		-t)\n'
                    '			t="$2"\n'
                    '			shift # past argument\n'
                    '			;;\n'
                    '		-r)\n'
                    '			r="$2"\n'
                    '			shift # past argument\n'
                    '			;;\n'
                    '		*)\n'
                    '			opts="$opts"" ""$key"" ""$2"\n'
                    '			shift # past argument\n'
                    '			;;\n'
                    '	esac\n'
                    '	shift # past argument or value\n'
                    'done\n'
                    '>&2 echo "info file \'$r\'"\n'
                    '>&2 echo "tree file \'$t\'"\n'
                    '>&2 echo "alignment file \'$a\'"\n'
                    'exit 1\n')
        chmod(fp_fake_sepp, 0o775)
        environ['PATH'] = '%s:%s' % (out_dir, self.oldpath)

        with self.assertRaisesRegex(CalledProcessError, ("'-r', '")):
            obs_tree, obs_placements = sepp(
                view,
                reference_alignment=ref_aln_small,
                reference_phylogeny=ref_phylo_small,
                reference_info=ref_info)


if __name__ == '__main__':
    unittest.main()
