# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

import qiime2.plugin
from qiime2.plugin import Citations
from q2_types.feature_data import FeatureData, Sequence, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency
from q2_types.tree import Phylogeny, Rooted

import q2_fragment_insertion
from q2_fragment_insertion._type import Placements, SeppReferenceDatabase
from q2_fragment_insertion._format import (
    PlacementsFormat, PlacementsDirFmt, SeppReferenceDirFmt, RAxMLinfoFormat)


citations = Citations.load('citations.bib', package='q2_fragment_insertion')

plugin = qiime2.plugin.Plugin(
    name='fragment-insertion',
    version=q2_fragment_insertion.__version__,
    website='https://github.com/qiime2/q2-fragment-insertion',
    short_description='Plugin for extending phylogenies.',
    package='q2_fragment_insertion',
    user_support_text='https://github.com/qiime2/q2-fragment-insertion/issues',
    citations=citations,
)


plugin.methods.register_function(
    function=q2_fragment_insertion.sepp,
    inputs={
        'representative_sequences': FeatureData[Sequence],
        'reference_database': SeppReferenceDatabase,
    },
    parameters={
        'threads': qiime2.plugin.Int,
        'alignment_subset_size': qiime2.plugin.Int,
        'placement_subset_size': qiime2.plugin.Int,
        'debug': qiime2.plugin.Bool,
    },
    outputs=[
        ('tree', Phylogeny[Rooted]),
        ('placements', Placements),
    ],
    input_descriptions={
        'representative_sequences': 'The sequences to insert into the '
                                    'reference tree.',
        'reference_database': 'The reference database to insert the '
                              'representative sequences into.',
    },
    parameter_descriptions={
        'threads': 'The number of threads to use.',
        'alignment_subset_size': 'Each placement subset is further broken '
                                 'into subsets of at most these many '
                                 'sequences and a separate HMM is trained on '
                                 'each subset.',
        'placement_subset_size': 'The tree is divided into subsets such that '
                                 'each subset includes at most these many '
                                 'subsets. The placement step places the '
                                 'fragment on only one subset, determined '
                                 'based on alignment scores. Further '
                                 'reading: https://github.com/smirarab/sepp/'
                                 'blob/master/tutorial/sepp-tutorial.md#sample'
                                 '-datasets-default-parameters.',
        'debug': 'Collect additional run information to STDOUT for debugging. '
                 'Temporary directories will not be removed if run fails.'
    },
    output_descriptions={
        'tree': 'The tree with inserted feature data.',
        'placements': 'Information about the feature placements within the '
                      'reference tree.',
    },
    name='Insert fragment sequences using SEPP into reference phylogenies.',
    description='Perform fragment insertion of sequences using the SEPP '
                'algorithm.',
)


plugin.methods.register_function(
    function=q2_fragment_insertion.classify_otus_experimental,
    inputs={
        'representative_sequences': FeatureData[Sequence],
        'tree': Phylogeny[Rooted],
        'reference_taxonomy': FeatureData[Taxonomy],
    },
    input_descriptions={
        'representative_sequences': 'The sequences used for a \'sepp\' run '
                                    'to produce the \'tree\'.',
        'tree': 'The tree resulting from inserting fragments into a reference '
                'phylogeny, i.e. the output of function \'sepp\'',
        'reference_taxonomy': 'Reference taxonomic table that maps every '
                              'OTU-ID into a taxonomic lineage string.',
    },
    parameters={},
    parameter_descriptions={},
    outputs=[
        ('classification', FeatureData[Taxonomy]),
    ],
    output_descriptions={
        'classification': 'Taxonomic lineages for inserted fragments.',
    },
    name='Experimental: Obtain taxonomic lineages, by finding closest OTU in '
         'reference phylogeny.',
    description='Experimental: Use the resulting tree from \'sepp\' and find '
                'closest OTU-ID for every inserted fragment. Then, look up '
                'the reference lineage string in the reference taxonomy.',
)


plugin.methods.register_function(
    function=q2_fragment_insertion.filter_features,
    inputs={
        'table': FeatureTable[Frequency],
        'tree': Phylogeny[Rooted],
    },
    input_descriptions={
        'table': 'A feature-table which needs to filtered down to those '
                 'fragments that are contained in the tree, e.g. result of a '
                 'Deblur or DADA2 run.',
        'tree': 'The tree resulting from inserting fragments into a reference '
                'phylogeny, i.e. the output of function \'sepp\'',
    },
    parameters={},
    parameter_descriptions={},
    outputs=[
        ('filtered_table', FeatureTable[Frequency]),
        ('removed_table', FeatureTable[Frequency]),
    ],
    output_descriptions={
        'filtered_table': 'The input table minus those fragments that were '
                          'not part of the tree. This feature-table can be '
                          'used for downstream analyses like phylogenetic '
                          'alpha- or beta- diversity computation.',
        'removed_table': 'Those fragments that got removed from the input '
                         'table, because they were not part of the tree. This '
                         'table is mainly used for quality control, e.g. to '
                         'inspect the ratio of removed reads per sample from '
                         'the input table. You can ignore this table for '
                         'downstream analyses.',
    },
    name='Filter fragments in tree from table.',
    description='Filters fragments not inserted into a phylogenetic tree from '
                'a feature-table. Some fragments computed by e.g. Deblur or '
                'DADA2 are too remote to get inserted by SEPP into a '
                'reference phylogeny. To be able to use the feature-table for '
                'downstream analyses like computing Faith\'s PD or UniFrac, '
                'the feature-table must be cleared of fragments that are not '
                'part of the phylogenetic tree, because their path length can '
                'otherwise not be determined. Typically, the number of '
                'rejected fragments is low (<= 10), but it might be worth to '
                'inspect the ratio of rea' 'ds assigned to those rejected '
                'fragments.',
)


# TODO: rough in method to merge database components
# TODO: rough in method to destructure database components


importlib.import_module('q2_fragment_insertion._transformer')


plugin.register_formats(PlacementsFormat, PlacementsDirFmt, RAxMLinfoFormat,
                        SeppReferenceDirFmt)
plugin.register_semantic_types(Placements, SeppReferenceDatabase)
plugin.register_semantic_type_to_format(Placements,
                                        artifact_format=PlacementsDirFmt)
plugin.register_semantic_type_to_format(SeppReferenceDatabase,
                                        artifact_format=SeppReferenceDirFmt)
