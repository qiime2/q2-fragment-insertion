# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os

import skbio
from q2_types.feature_data import DNAIterator


def _sanity():
    if shutil.which('java') is None:
        raise ValueError("java does not appear in $PATH")

    sepp = _sepp_path()
    if not os.path.exists(sepp):
        raise ValueError("Cannot find run-sepp.sh, expected it at: %s" % sepp)


def _sepp_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'assests/sepp-package/run-sepp.sh')


def _run(seqs_fp, threads):
    cmd = [_sepp_path(),
           seqs_fp,
           'q2-fragment-insertion',
           '-x', threads],

    subprocess.run(cmd, check=True)


def sepp_16s_greengenes(representative_sequences: DNAIterator
                        threads: int=1) -> skbio.TreeNode:

    _sanity()

    current = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        _run(str(representative_sequences), str(threads))
        outfile = 'q2-fragment-insertion_placement.tog.tre'
        return skbio.TreeNode.read(outfile)
