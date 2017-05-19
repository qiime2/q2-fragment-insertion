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
from q2_types import Int

import q2_fragment_insertion as q2fi


plugin = qiime2.plugin.Plugin(
    name='fragment-insertion',
    version=q2fi.__version__,
    website='https://github.com/wasade/q2-fragment-insertion',
    package='q2_fragment_insertion',
    user_support_text='https://github.com/wasade/q2-fragment-insertion/issues',
    citation_text=("what should go here? SEPP??")
)


_parameter_descriptions = {'threads': 'The number of threads to use'
}


_output_descriptions = {'tree': 'The tree with inserted feature data'
}


_parameters = {'threads': Int}


_outputs = [('tree', Phylogeny[Rooted])]


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
