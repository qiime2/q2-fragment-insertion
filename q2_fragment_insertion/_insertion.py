# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import sys
import shutil
import tempfile
import subprocess
from pkg_resources import resource_exists, Requirement, resource_filename

import skbio
import pandas as pd
import numpy as np
from q2_types.feature_data import (DNASequencesDirectoryFormat,
                                   DNAFASTAFormat,
                                   DNAIterator,
                                   AlignedDNASequencesDirectoryFormat,
                                   AlignedDNAIterator,
                                   AlignedDNAFASTAFormat)
from qiime2.sdk import Artifact
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


def _obtain_taxonomy(filename_tree: str,
                     representative_sequences:
                     DNASequencesDirectoryFormat) -> pd.DataFrame:
    """Buttom up traverse tree for nodes that are inserted fragments and
       collect taxonomic labels upon traversal."""
    tree = skbio.TreeNode.read(str(filename_tree))
    taxonomy = []
    for fragment in representative_sequences.file.view(DNAIterator):
        lineage = []
        try:
            for ancestor in tree.find(fragment.metadata['id']).ancestors():
                if (ancestor.name is not None) and ('__' in ancestor.name):
                    lineage.append(ancestor.name)
            lineage_str = '; '.join(reversed(lineage))
        except skbio.tree.MissingNodeError:
            lineage_str = np.nan
        taxonomy.append({'Feature ID': fragment.metadata['id'],
                         'Taxon': lineage_str})
    pd_taxonomy = pd.DataFrame(taxonomy).set_index('Feature ID')
    if pd_taxonomy['Taxon'].dropna().shape[0] == 0:
        raise ValueError(
            ("None of the representative-sequences can be found in the "
             "insertion tree. Please double check that both inputs match up, "
             "i.e. are results from the same 'sepp' run."))
    return pd_taxonomy


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


def sepp(representative_sequences: DNASequencesDirectoryFormat,
         threads: int=1,
         reference_alignment: AlignedDNASequencesDirectoryFormat=None,
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
        _run(str(representative_sequences.file.view(DNAFASTAFormat)),
             str(threads), tmp,
             reference_alignment, reference_phylogeny)
        outtree = os.path.join(tmp, tree)
        outplacements = os.path.join(tmp, placements)

        _add_missing_branch_length(outtree)

        shutil.copyfile(outtree, str(tree_result))
        shutil.copyfile(outplacements, str(placements_result))

    return tree_result, placements_result


def classify_paths(representative_sequences: DNASequencesDirectoryFormat,
                   tree: NewickFormat) -> pd.DataFrame:
    return _obtain_taxonomy(str(tree), representative_sequences)


def classify_otus(representative_sequences: DNASequencesDirectoryFormat,
                  tree: NewickFormat,
                  reference_taxonomy: pd.DataFrame=None) -> pd.DataFrame:
    if reference_taxonomy is None:
        filename_default_taxonomy = resource_filename(
            Requirement.parse('q2_fragment_insertion'),
            os.path.join('q2_fragment_insertion/assets/', 'taxonomy_gg99.qza'))
        reference_taxonomy = Artifact.load(
            filename_default_taxonomy).view(pd.DataFrame)

    # convert type of feature IDs to str (depending on pandas type inference
    # they might come as integers), to make sure they are of the same type as
    # in the tree.
    reference_taxonomy.index = map(str, reference_taxonomy.index)

    # load the insertion tree
    tree = skbio.TreeNode.read(str(tree))

    # ensure that all reference tips in the tree (those without the inserted
    # fragments) have a mapping in the user provided taxonomy table
    names_tips = set([node.name for node in tree.tips()])
    names_fragments = set([fragment.metadata['id']
                           for fragment
                           in representative_sequences.file.view(DNAIterator)])
    missing_features = (set(names_tips) - set(names_fragments)) -\
        set(reference_taxonomy.index)
    if len(missing_features) > 0:
        # QIIME2 users can run with --verbose and see stderr and stdout.
        # Thus, we here report more details about the mismatch:
        sys.stderr.write(
            ("The taxonomy artifact you provided does not contain lineage "
             "information for the following %i features:\n%s") %
            (len(missing_features), "\n".join(missing_features)))
        raise ValueError("Not all OTUs in the provided insertion tree have "
                         "mappings in the provided reference taxonomy.")

    taxonomy = []
    for fragment in representative_sequences.file.view(DNAIterator):
        lineage_str = np.nan
        try:
            curr_node = tree.find(fragment.metadata['id'])
            foundOTUs = []
            while len(foundOTUs) == 0:
                for node in curr_node.postorder():
                    if (node.name is not None) and \
                       (node.name in reference_taxonomy.index):
                        foundOTUs.append(node.name)
                if curr_node.is_root():
                    break
                curr_node = curr_node.parent
            if len(foundOTUs) > 0:
                split_lineages = []
                for otu in foundOTUs:
                    # find lineage string for OTU
                    lineage = reference_taxonomy.loc[otu, 'Taxon']
                    # necessary to split lineage apart to ensure that
                    # the longest common prefix operates on atomic ranks
                    # instead of characters
                    split_lineages.append(list(
                        map(str.strip, lineage.split(';'))))
                # find the longest common prefix rank-wise and concatenate to
                # one lineage string, separated by ;
                lineage_str = "; ".join(os.path.commonprefix(split_lineages))
        except skbio.tree.MissingNodeError:
            pass
        taxonomy.append({'Feature ID': fragment.metadata['id'],
                         'Taxon': lineage_str})
    pd_taxonomy = pd.DataFrame(taxonomy).set_index('Feature ID')
    if pd_taxonomy['Taxon'].dropna().shape[0] == 0:
        raise ValueError(
            ("None of the representative-sequences can be found in the "
             "insertion tree. Please double check that both inputs match up, "
             "i.e. are results from the same 'sepp' run."))

    return pd_taxonomy
