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
from q2_types.feature_data import (DNAFASTAFormat,
                                   AlignedDNASequencesDirectoryFormat,
                                   AlignedDNAIterator,
                                   AlignedDNAFASTAFormat)
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


def _reference_matches(reference_alignment:
                       AlignedDNASequencesDirectoryFormat=None,
                       reference_phylogeny: NewickFormat=None) -> bool:
    dir_sepp_ref = 'q2_fragment_insertion/assets/sepp-package/ref/'

    # no check neccessary when user does not provide specific references,
    # because we assume that the default reference matches.
    if (reference_alignment is None) and (reference_phylogeny is None):
        return True

    # if only phylogeny is provided by the user, load default alignment
    if reference_alignment is None:
        filename_alignment = resource_filename(
            Requirement.parse('q2_fragment_insertion'),
            os.path.join(dir_sepp_ref, 'gg_13_5_ssu_align_99_pfiltered.fasta'))
        ids_alignment = {
            row.metadata['id']
            for row in skbio.alignment.TabularMSA.read(
                filename_alignment,
                format='fasta', constructor=skbio.sequence.DNA)}
    else:
        ids_alignment = {
            row.metadata['id']
            for row in reference_alignment.file.view(AlignedDNAIterator)}

    # if only alignment is provided by the user, load default phylogeny
    if reference_phylogeny is None:
        filename_phylogeny = resource_filename(
            Requirement.parse('q2_fragment_insertion'),
            os.path.join(dir_sepp_ref,
                         'reference-gg-raxml-bl-rooted-relabelled.tre'))
    else:
        filename_phylogeny = str(reference_phylogeny)
    ids_tips = {node.name
                for node in skbio.TreeNode.read(filename_phylogeny).tips()}

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
         reference_alignment: AlignedDNASequencesDirectoryFormat=None,
         reference_phylogeny: NewickFormat=None):
    cmd = [_sepp_path(),
           seqs_fp,
           'q2-fragment-insertion',
           '-x', str(threads)]
    if reference_alignment is not None:
        cmd.extend([
            '-a', str(reference_alignment.file.view(AlignedDNAFASTAFormat))])
    if reference_phylogeny is not None:
        cmd.extend(['-t', str(reference_phylogeny)])

    subprocess.run(cmd, check=True, cwd=cwd)


def sepp_16s_greengenes(representative_sequences: DNAFASTAFormat,
                        threads: int=1,
                        reference_alignment:
                        AlignedDNASequencesDirectoryFormat=None,
                        reference_phylogeny: NewickFormat=None
                        ) -> (NewickFormat, PlacementsFormat):

    _sanity()
    # check if sequences and tips in reference match
    if not _reference_matches(reference_alignment, reference_phylogeny):
        raise ValueError(
            ('Reference alignment and phylogeny do not match up. Please ensure'
             ' that all sequences in the alignment correspond to exactly one '
             'tip name in the phylogeny.'))

    placements = 'q2-fragment-insertion_placement.json'
    tree = 'q2-fragment-insertion_placement.tog.relabelled.tre'

    placements_result = PlacementsFormat()
    tree_result = NewickFormat()

    with tempfile.TemporaryDirectory() as tmp:
        _run(str(representative_sequences), str(threads), tmp,
             reference_alignment, reference_phylogeny)
        outtree = os.path.join(tmp, tree)
        outplacements = os.path.join(tmp, placements)

        _add_missing_branch_length(outtree)

        shutil.copyfile(outtree, str(tree_result))
        shutil.copyfile(outplacements, str(placements_result))

    return tree_result, placements_result
