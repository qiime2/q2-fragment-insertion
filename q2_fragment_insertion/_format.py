# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import ijson

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

from q2_types.feature_data import AlignedDNAFASTAFormat
from q2_types.tree import NewickFormat


class PlacementsFormat(model.TextFileFormat):
    fields = {'tree', 'placements', 'metadata', 'invocation',
              'version', 'fields'}

    def _validate_(self, level):
        keys_found = set()

        # Can't self.open(mode='rb'), so we defer to the backing pathlib object
        with self.path.open(mode='rb') as fh:
            for prefix, event, value in ijson.parse(fh):
                # TODO: check that root structure is a map
                if prefix.startswith('placements') \
                        or prefix.startswith('tree'):
                    continue
                # TODO: probably need to restrict this to root-level keys
                if event == 'map_key':
                    keys_found.add(value)

        if keys_found != self.fields:
            raise ValidationError('Expected the following fields: %s, found '
                                  '%s.' % (self.fields, keys_found))


PlacementsDirFmt = model.SingleFileDirectoryFormat(
    'PlacementsDirFmt', 'placements.json', PlacementsFormat)


# TODO: Format tests
class RAxMLinfoFormat(model.TextFileFormat):
    # TODO https://github.com/smirarab/sepp/blob/master/sepp-package/buildref/
    # reformat-info.py
    def _validate_(self, level):
        pass


# TODO: Format tests
class SeppReferenceFormat(model.DirectoryFormat):
    alignment = model.File(r'aligned-dna-sequences.fasta',
                           format=AlignedDNAFASTAFormat)
    phylogeny = model.File(r'tree.nwk', format=NewickFormat)
    raxml_info = model.File(r'raxml-info.txt', format=RAxMLinfoFormat)

    def _validate_(self, level):
        pass
