# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

import qiime2.plugin
from q2_types.feature_data import FeatureData, Sequence
from q2_types.tree import Phylogeny, Rooted

import q2_fragment_insertion as q2fi
from q2_fragment_insertion._type import Placements
from q2_fragment_insertion._format import (PlacementsFormat, PlacementsDirFmt)


plugin = qiime2.plugin.Plugin(
    name='fragment-insertion',
    version=q2fi.__version__,
    website='https://github.com/wasade/q2-fragment-insertion',
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

_parameter_descriptions = {'threads': 'The number of threads to use'
}


_output_descriptions = {'tree': 'The tree with inserted feature data'
}


_parameters = {'threads': qiime2.plugin.Int}


_outputs = [('tree', Phylogeny[Rooted]),
            ('placements', Placements)]


plugin.methods.register_function(
    function=q2fi.sepp_16s_greengenes,
    inputs={'representative_sequences': FeatureData[Sequence]},
    parameters=_parameters,
    outputs=_outputs,
    input_descriptions={'representative_sequences': "The sequences to insert"},
    parameter_descriptions=_parameter_descriptions,
    output_descriptions=_output_descriptions,
    name='Insert fragment 16S sequences using SEPP into Greengenes 13_8',
    description=('Perform fragment insertion of 16S sequences using the SEPP '
                 'algorithm against the Greengenes 13_8 99% tree.')
)


importlib.import_module('q2_fragment_insertion._transformer')
