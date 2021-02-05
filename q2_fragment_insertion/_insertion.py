# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import tempfile
import subprocess

import skbio
import biom
import pandas as pd
import numpy as np
from q2_types.feature_data import (DNASequencesDirectoryFormat,
                                   DNAFASTAFormat,
                                   DNAIterator)
from q2_types.tree import NewickFormat

from q2_fragment_insertion._format import PlacementsFormat, SeppReferenceDirFmt


# Beta-diversity computation often requires every branch to have a length,
# which is not necessarily true for SEPP produced insertion trees. We add zero
# branch length information for branches without an explicit length.
def _add_missing_branch_length(tree_fp):
    tree = skbio.TreeNode.read(tree_fp)
    for node in tree.preorder():
        if node.length is None:
            node.length = 0
    tree.write(tree_fp)


def _run(seqs_fp, threads, cwd, alignment_subset_size, placement_subset_size,
         reference_alignment, reference_phylogeny,
         reference_info, debug=False):
    cmd = ['run-sepp.sh',
           seqs_fp,
           'q2-fragment-insertion',
           '-x', str(threads),
           '-A', str(alignment_subset_size),
           '-P', str(placement_subset_size),
           '-a', reference_alignment,
           '-t', reference_phylogeny,
           '-r', reference_info,
           ]
    if debug:
        cmd.extend(['-b', '1'])

    subprocess.run(cmd, check=True, cwd=cwd)


def sepp(representative_sequences: DNASequencesDirectoryFormat,
         reference_database: SeppReferenceDirFmt,
         alignment_subset_size: int = 1000,
         placement_subset_size: int = 5000,
         threads: int = 1,
         debug: bool = False,
         ) -> (NewickFormat, PlacementsFormat):

    placements = 'q2-fragment-insertion_placement.json'
    tree = 'q2-fragment-insertion_placement.tog.relabelled.tre'

    placements_result = PlacementsFormat()
    tree_result = NewickFormat()

    with tempfile.TemporaryDirectory() as tmp:
        _run(str(representative_sequences.file.view(DNAFASTAFormat)),
             str(threads), tmp,
             str(alignment_subset_size), str(placement_subset_size),
             str(reference_database.alignment.path_maker()),
             str(reference_database.phylogeny.path_maker()),
             str(reference_database.raxml_info.path_maker()),
             debug)
        outtree = os.path.join(tmp, tree)
        outplacements = os.path.join(tmp, placements)

        _add_missing_branch_length(outtree)

        shutil.copyfile(outtree, str(tree_result))
        shutil.copyfile(outplacements, str(placements_result))

    return tree_result, placements_result


def classify_paths(representative_sequences: DNASequencesDirectoryFormat,
                   tree: NewickFormat) -> pd.DataFrame:
    # Traverse trees from bottom-up for nodes that are inserted fragments and
    # collect taxonomic labels upon traversal.
    tree = skbio.TreeNode.read(str(tree))
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
            ('None of the representative-sequences can be found in the '
             'insertion tree. Please double check that both inputs match up, '
             'i.e. are results from the same \'sepp\' run.'))
    return pd_taxonomy


def classify_otus_experimental(
        representative_sequences: DNASequencesDirectoryFormat,
        tree: NewickFormat,
        reference_taxonomy: pd.DataFrame) -> pd.DataFrame:

    # convert type of feature IDs to str (depending on pandas type inference
    # they might come as integers), to make sure they are of the same type as
    # in the tree.
    reference_taxonomy.index = map(str, reference_taxonomy.index)

    # load the insertion tree
    tree = skbio.TreeNode.read(str(tree))

    # ensure that all reference tips in the tree (those without the inserted
    # fragments) have a mapping in the user provided taxonomy table
    names_tips = {node.name for node in tree.tips()}
    names_fragments = {fragment.metadata['id']
                       for fragment
                       in representative_sequences.file.view(DNAIterator)}
    missing_features = (names_tips - names_fragments) -\
        set(reference_taxonomy.index)
    if len(missing_features) > 0:
        raise ValueError("Not all OTUs in the provided insertion tree have "
                         "mappings in the provided reference taxonomy. "
                         "Taxonomy missing for the following %i feature(s):"
                         "\n%s" % (len(missing_features),
                                   "\n".join(missing_features)))

    taxonomy = []
    for fragment in representative_sequences.file.view(DNAIterator):
        # for every inserted fragment we now try to find the closest OTU tip
        # in the tree and available mapping from the OTU-ID to a lineage
        # string:
        lineage_str = np.nan
        # first, let us check if the fragment has been inserted at all ...
        try:
            curr_node = tree.find(fragment.metadata['id'])
        except skbio.tree.MissingNodeError:
            continue
        # if yes, we start from the inserted node and traverse the tree as less
        # as possible towards the root and check at every level if one or
        # several OTU-tips are within the sub-tree.
        if curr_node is not None:
            foundOTUs = []
            # Traversal is stopped at a certain level, if one or more OTU-tips
            # have been found in the sub-tree OR ... (see break below)
            while len(foundOTUs) == 0:
                # SEPP insertion - especially for multiple very similar
                # sequences - can result in a rather complex topology change
                # if all those sequences are inserted into the same branch
                # leading to one OTU-tip. Thus, we cannot simply visit only
                # all siblings or decendents and rather need to traverse the
                # whole sub-tree. Average case should be well behaved,
                # thus I think it is ok.
                for node in curr_node.postorder():
                    if (node.name is not None) and \
                       (node.name in reference_taxonomy.index):
                        # if a suitable OTU-tip node is found AND this OTU-ID
                        # has a mapping in the user provided reference_taxonomy
                        # we store the OTU-ID in the growing result list
                        foundOTUs.append(node.name)
                # ... if the whole tree has been traversed without success,
                # e.g. if user provided reference_taxonomy did not contain any
                # matching OTU-IDs.
                if curr_node.is_root():
                    break
                # prepare next while iteration, by changing to the parent node
                curr_node = curr_node.parent

            if len(foundOTUs) > 0:
                # If the above method has identified exactly one OTU-tip,
                # resulting lineage string would simple be the one provided by
                # the user reference_taxonomy. However, if the inserted
                # fragment cannot unambiguously places into the reference tree,
                # the above method will find multiple OTU-IDs, which might have
                # lineage strings in the user provided reference_taxonomy that
                # are similar up to a certain rank and differ e.g. for genus
                # and species.
                # Thus, we here find the longest common prefix of all lineage
                # strings. We don't operate per character, but per taxonomic
                # rank. Therefore, we first "convert" every lineage sting into
                # a list of taxa, one per rank.
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
            taxonomy.append({'Feature ID': fragment.metadata['id'],
                             'Taxon': lineage_str})
    pd_taxonomy = pd.DataFrame(taxonomy)
    # test if dataframe is completely empty, or if no lineages could be found
    if (len(taxonomy) == 0) or \
       (pd_taxonomy['Taxon'].dropna().shape[0] == 0):
        raise ValueError(
            ("None of the representative-sequences can be found in the "
             "insertion tree. Please double check that both inputs match up, "
             "i.e. are results from the same 'sepp' run."))

    return pd_taxonomy.set_index('Feature ID')


def filter_features(table: biom.Table,
                    tree: NewickFormat) -> (biom.Table, biom.Table):

    # load the insertion tree
    tree = skbio.TreeNode.read(str(tree))
    # collect all tips=inserted fragments+reference taxa names
    fragments_tree = {
        str(tip.name)
        for tip in tree.tips()
        if tip.name is not None}

    # collect all fragments/features from table
    fragments_table = set(map(str, table.ids(axis='observation')))

    if len(fragments_table & fragments_tree) <= 0:
        raise ValueError(('Not a single fragment of your table is part of your'
                          ' tree. The resulting table would be empty.'))

    tbl_positive = table.filter(fragments_table & fragments_tree,
                                axis='observation', inplace=False)
    tbl_negative = table.filter(fragments_table - fragments_tree,
                                axis='observation', inplace=False)

    # print some information for quality control,
    # which user can request via --verbose
    results = pd.DataFrame(
        data={'kept_reads': tbl_positive.sum(axis='sample'),
              'removed_reads': tbl_negative.sum(axis='sample')},
        index=tbl_positive.ids())
    results['removed_ratio'] = results['removed_reads'] / \
        (results['kept_reads'] + results['removed_reads'])

    return (tbl_positive, tbl_negative)
