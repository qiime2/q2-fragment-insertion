# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

import qiime2.plugin
from qiime2.plugin import Citations
from q2_types.feature_data import (FeatureData, Sequence, AlignedSequence,
                                   Taxonomy)
from q2_types.feature_table import (FeatureTable, Frequency)
from q2_types.tree import Phylogeny, Rooted

import q2_fragment_insertion as q2fi
from q2_fragment_insertion._type import Placements
from q2_fragment_insertion._format import (PlacementsFormat, PlacementsDirFmt)

citations = Citations.load('citations.bib', package='q2_fragment_insertion')
plugin = qiime2.plugin.Plugin(
    name='fragment-insertion',
    version=q2fi.__version__,
    website='https://github.com/biocore/q2-fragment-insertion',
    short_description='Plugin for extending phylogenies.',
    package='q2_fragment_insertion',
    user_support_text=('https://github.com/biocore/'
                       'q2-fragment-insertion/issues'),
    citation_text=('Stefan Janssen, Daniel McDonald, Antonio Gonzalez, '
                   'Jose A. Navas-Molina, Lingjing Jiang, '
                   'Zhenjiang Zech Xu, Kevin Winker, Deborah M. Kado, '
                   'Eric Orwoll, Mark Manary, Siavash Mirarab, Rob Knight.'
                   ' "Phylogenetic Placement of Exact Amplicon Sequences '
                   'Improves Associations with Clinical Information." '
                   'mSystems. 2018.')
)


plugin.register_formats(PlacementsFormat, PlacementsDirFmt)
plugin.register_semantic_types(Placements)
plugin.register_semantic_type_to_format(Placements,
                                        artifact_format=PlacementsDirFmt)

_parameter_descriptions = {
    'threads': 'The number of threads to use',
    'alignment_subset_size':
    ('Each placement subset is further broken into subsets of at most these '
     'many sequences and a separate HMM is trained on each subset. The '
     'default alignment subset size is set to balance the exhaustiveness of '
     'the alignment step with the running time.'),
    'placement_subset_size':
    ('The tree is divided into subsets such that each subset includes at most '
     'these many subsets. The placement step places the fragment on only one '
     'subset, determined based on alignment scores. The default placement '
     'subset is set to make sure the memory requirement of the pplacer step '
     'does not become prohibitively large.\nFurther reading: '
     'https://github.com/smirarab/sepp/blob/master/tutorial/sepp-tutorial.md'
     '#sample-datasets-default-parameters')}

_output_descriptions = {
    'tree': 'The tree with inserted feature data'}


_parameters = {'threads': qiime2.plugin.Int,
               'alignment_subset_size': qiime2.plugin.Int,
               'placement_subset_size': qiime2.plugin.Int
               }


_outputs = [('tree', Phylogeny[Rooted]),
            ('placements', Placements)]


plugin.methods.register_function(
    function=q2fi.sepp,
    inputs={'representative_sequences': FeatureData[Sequence],
            'reference_alignment': FeatureData[AlignedSequence],
            'reference_phylogeny': Phylogeny[Rooted]},
    parameters=_parameters,
    outputs=_outputs,
    input_descriptions={
        'representative_sequences': "The sequences to insert",
        'reference_alignment':
        ('The reference multiple nucleotide alignment used '
         'to construct the reference phylogeny.'),
        'reference_phylogeny':
        ('The rooted reference phylogeny. Must be in sync '
         'with reference-alignment, i.e. each tip name must'
         ' have exactly one corresponding record.')},
    parameter_descriptions=_parameter_descriptions,
    output_descriptions=_output_descriptions,
    name=('Insert fragment sequences using SEPP into reference phylogenies '
          'like Greengenes 13_8'),
    description=('Perform fragment insertion of 16S sequences using the SEPP '
                 'algorithm against the Greengenes 13_8 99% tree.'),
    citations=[citations['SEPP']]
)


# plugin.methods.register_function(
#     function=q2fi.classify_paths,
#     inputs={'representative_sequences': FeatureData[Sequence],
#             'tree': Phylogeny[Rooted]},
#     input_descriptions={
#         'representative_sequences':
#         "The sequences used for a \'sepp\' run to produce the \'tree\'.",
#         'tree':
#         ('The tree resulting from inserting fragments into a reference '
#          'phylogeny, i.e. the output of function \'sepp\'')},
#     parameters={},
#     parameter_descriptions={},
#     outputs=[('classification', FeatureData[Taxonomy])],
#     output_descriptions={
#         'classification': 'Taxonomic lineages for inserted fragments.'},
#     name=('Obtain taxonomic lineages, by collecting taxonomic labels from '
#           'reference phylogeny.'),
#     description=(
#         ('Use the resulting tree from \'sepp\' and traverse it bottom-up to '
#          'obtain taxonomic lineages for every inserted fragment. Only works '
#          'for Greengenes lines labels, i.e. they need to contain "__" '
#          'infixes. Quality strongly depends on correct placements of'
#          'taxonomic labels in the provided reference phylogeny.'))
# )


plugin.methods.register_function(
    function=q2fi.classify_otus_experimental,
    inputs={'representative_sequences': FeatureData[Sequence],
            'tree': Phylogeny[Rooted],
            'reference_taxonomy': FeatureData[Taxonomy]},
    input_descriptions={
        'representative_sequences':
        "The sequences used for a \'sepp\' run to produce the \'tree\'.",
        'tree':
        ('The tree resulting from inserting fragments into a reference '
         'phylogeny, i.e. the output of function \'sepp\''),
        'reference_taxonomy':
        ("Reference taxonomic table that maps every OTU-ID into a taxonomic "
         "lineage string.")},
    parameters={},
    parameter_descriptions={},
    outputs=[('classification', FeatureData[Taxonomy])],
    output_descriptions={
        'classification': 'Taxonomic lineages for inserted fragments.'},
    name=('Experimental: Obtain taxonomic lineages, by finding closest OTU in '
          'reference phylogeny.'),
    description=(
        'Experimental: Use the resulting tree from \'sepp\' and find closest '
        'OTU-ID for every inserted fragment. Then, look up the reference '
        'lineage string in the reference taxonomy.')
)


plugin.methods.register_function(
    function=q2fi.filter_features,
    inputs={'table': FeatureTable[Frequency],
            'tree': Phylogeny[Rooted]},
    input_descriptions={
        'table':
        ("A feature-table which needs to filtered down to those fragments that"
         " are contained in the tree, e.g. result of a Deblur or DADA2 run."),
        'tree':
        ('The tree resulting from inserting fragments into a reference '
         'phylogeny, i.e. the output of function \'sepp\''),
        },
    parameters={},
    parameter_descriptions={},
    outputs=[('filtered_table', FeatureTable[Frequency]),
             ('removed_table', FeatureTable[Frequency])],
    output_descriptions={
        'filtered_table':
        ('The input table minus those fragments that were not part of the tree'
         '. This feature-table can be used for downstream analyses like '
         'phylogenetic alpha- or beta- diversity computation.'),
        'removed_table':
        ('Those fragments that got removed from the input table, because they '
         'were not part of the tree. This table is mainly used for quality '
         'control, e.g. to inspect the ratio of removed reads per sample from'
         ' the input table. You can ignore this table for downstream '
         'analyses.')},
    name=("Filter fragments in tree from table."),
    description=(
        'Filters fragments not inserted into a phylogenetic tree from a featu'
        're-table. Some fragments computed by e.g. Deblur or DADA2 are too rem'
        'ote to get inserted by SEPP into a reference phylogeny. To be able to'
        ' use the feature-table for downstream analyses like computing Faith\''
        's PD or UniFrac, the feature-table must be cleared of fragments that '
        'are not part of the phylogenetic tree, because their path length can '
        'otherwise not be determined. Typically, the number of rejected fragme'
        'nts is low (<= 10), but it might be worth to inspect the ratio of rea'
        'ds assigned to those rejected fragments.')
)


importlib.import_module('q2_fragment_insertion._transformer')
