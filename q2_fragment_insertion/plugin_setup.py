# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

import qiime2.plugin
from q2_types.feature_data import (FeatureData, Sequence, AlignedSequence,
                                   Taxonomy)
from q2_types.tree import Phylogeny, Rooted

import q2_fragment_insertion as q2fi
from q2_fragment_insertion._type import Placements
from q2_fragment_insertion._format import (PlacementsFormat, PlacementsDirFmt)


plugin = qiime2.plugin.Plugin(
    name='fragment-insertion',
    version=q2fi.__version__,
    website='https://github.com/wasade/q2-fragment-insertion',
    short_description='Plugin for extending phylogenies.',
    package='q2_fragment_insertion',
    user_support_text='https://github.com/wasade/q2-fragment-insertion/issues',
    citation_text=('Mirarab, Siavash, Nam Nguyen, and Tandy J. Warnow. "SEPP: '
                   'SATé-enabled phylogenetic placement." Pacific Symposium '
                   'on Biocomputing. 2012."')
)


plugin.register_formats(PlacementsFormat, PlacementsDirFmt)
plugin.register_semantic_types(Placements)
plugin.register_semantic_type_to_format(Placements,
                                        artifact_format=PlacementsDirFmt)

_parameter_descriptions = {'threads': 'The number of threads to use'}


_output_descriptions = {
    'tree': 'The tree with inserted feature data'}


_parameters = {'threads': qiime2.plugin.Int}


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
                 'algorithm against the Greengenes 13_8 99% tree.')
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


importlib.import_module('q2_fragment_insertion._transformer')
