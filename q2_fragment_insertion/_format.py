# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model

from q2_types.feature_data import AlignedDNAFASTAFormat
from q2_types.tree import NewickFormat


# TODO: Format tests
class PlacementsFormat(model.TextFileFormat):
    # TODO: replace with a robust validate method
    def sniff(self):
        line = open(str(self)).readline()

        # it's json... but would be very expensive to parse
        return line[0] == '{'


PlacementsDirFmt = model.SingleFileDirectoryFormat(
    'PlacementsDirFmt', 'placements.json', PlacementsFormat)


# TODO: Format tests
class RAxMLinfoFormat(model.TextFileFormat):
    # TODO: replace with a robust validate method
    # https://github.com/smirarab/sepp/blob/master/sepp-package/buildref/reformat-info.py
    def sniff(self):
        return True


# TODO: Format tests
class SeppReferenceFormat(model.DirectoryFormat):
    alignment = model.File(
        r'aligned-dna-sequences.fasta', format=AlignedDNAFASTAFormat)
    phylogeny = model.File(r'tree.nwk', format=NewickFormat)
    raxml_info = model.File(r'raxml-info.txt', format=RAxMLinfoFormat)
