# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import tempfile
import subprocess
from pkg_resources import resource_exists, Requirement, resource_filename

import skbio
from q2_types.feature_data import DNAFASTAFormat, AlignedDNAFASTAFormat
from q2_types.tree import NewickFormat

from q2_fragment_insertion._format import PlacementsFormat

# adapted from q2-state-unifrac
ARGS = (Requirement.parse('q2_fragment_insertion'),
        'q2_fragment_insertion/assets/sepp-package/run-sepp.sh')


def _sanity():
    if shutil.which('java') is None:
        raise ValueError("java does not appear in $PATH")
    if not resource_exists(*ARGS):
        raise ValueError("ssu could not be located!")


def _reference_matches(reference_alignment: skbio.alignment.TabularMSA=None,
                       reference_phylogeny: skbio.TreeNode=None) -> bool:
    dir_sepp_ref = 'q2_fragment_insertion/assets/sepp-package/ref/'

    # no check neccessary when user does not provide specific references,
    # because we assume that the default reference matches.
    if (reference_alignment is None) and (reference_phylogeny is None):
        return True

    # if only phylogeny is provided by the user, load default alignment
    if (reference_alignment is None) and (reference_phylogeny is not None):
        reference_alignment = skbio.alignment.TabularMSA.read(os.path.join(
            dir_sepp_ref, 'gg_13_5_ssu_align_99_pfiltered.fasta'),
            format='fasta', constructor=DNA)

    # if only alignment is provided by the user, load default phylogeny
    if (reference_alignment is not None) and (reference_phylogeny is None):
        reference_phylogeny = TreeNode.read(os.path.join(
            dir_sepp_ref, 'reference-gg-raxml-bl-rooted-relabelled.tre'))

    # collect all sequence names from alignment and tip names from phylogeny
    ids_alignment = {row.metadata['id'] for row in reference_alignment}
    ids_tips = {node.name for node in reference_phylogeny.tips()}

    # both id sets need to match
    return ids_alignment == ids_tips


def _add_missing_branch_length(filename_tree):
    """Beta-diversity computation with Qiime2 requires every branch to have a
       length, which is not necessarily true for SEPP produced insertion trees.
       Thus we add zero branch length information for branches without an
       explicit length."""

    tree = skbio.TreeNode.read(filename_tree)
    for node in tree.preorder():
        if node.length is None:
            node.length = 0
    tree.write(filename_tree)


def _sepp_path():
    return resource_filename(*ARGS)


def _run(seqs_fp, threads, cwd,
         filename_ref_alignment=None, filename_ref_phylogeny=None):
    cmd = [_sepp_path(),
           seqs_fp,
           'q2-fragment-insertion',
           '-x', str(threads)]
    if filename_ref_alignment is not None:
        cmd.extend(['-a', os.path.join(cwd, filename_ref_alignment)])
    if filename_ref_phylogeny is not None:
        cmd.extend(['-t', os.path.join(cwd, filename_ref_phylogeny)])

    subprocess.run(cmd, check=True, cwd=cwd)


def sepp_16s_greengenes(representative_sequences: DNAFASTAFormat,
                        threads: int=1,
                        reference_alignment: skbio.alignment.TabularMSA=None,
                        reference_phylogeny: skbio.TreeNode=None
                        ) -> (NewickFormat, PlacementsFormat):

    _sanity()
    # check if sequences and tips in reference match
    if not _reference_matches(reference_alignment, reference_phylogeny):
        raise ValueError(
            ('Reference alignment and phylogeny don\'t match up. Please ensure'
             ' that all sequences in the alignment correspond to exactly one '
             'tip name in the phylogeny.'))

    placements = 'q2-fragment-insertion_placement.json'
    tree = 'q2-fragment-insertion_placement.tog.relabelled.tre'

    placements_result = PlacementsFormat()
    tree_result = NewickFormat()

    with tempfile.TemporaryDirectory() as tmp:
        # write reference alignment and phylogeny to tmp dir if provided by
        # the user
        filename_ref_alignment = None
        if reference_alignment is not None:
            filename_ref_alignment = 'reference_alignment.fasta'
            reference_alignment.write(
                os.path.join(tmp, filename_ref_alignment), format='fasta')
        filename_ref_phylogeny = None
        if reference_phylogeny is not None:
            filename_ref_phylogeny = 'reference_phylogeny.nwk'
            reference_phylogeny.write(
                os.path.join(tmp, filename_ref_phylogeny))

        _run(str(representative_sequences), str(threads), tmp,
             filename_ref_alignment, filename_ref_phylogeny)
        outtree = os.path.join(tmp, tree)
        outplacements = os.path.join(tmp, placements)

        _add_missing_branch_length(outtree)

        shutil.copyfile(outtree, str(tree_result))
        shutil.copyfile(outplacements, str(placements_result))

    return tree_result, placements_result
