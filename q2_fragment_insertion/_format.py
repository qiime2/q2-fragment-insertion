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

import skbio


class PlacementsFormat(model.TextFileFormat):
    fields = {'tree', 'placements', 'metadata', 'version', 'fields'}

    def _validate_(self, level):
        keys_found = set()

        # Can't self.open(mode='rb'), so we defer to the backing pathlib object
        with self.path.open(mode='rb') as fh:
            root_element = None
            for prefix, event, value in ijson.parse(fh):
                if root_element is None:
                    if event != 'start_map':
                        raise ValidationError('Root element of file must be a '
                                              'JSON object')
                    else:
                        root_element = True

                # Skip parsing attributes that could be prohibitively large
                if prefix.startswith('placements') \
                        or prefix.startswith('tree'):
                    continue

                # Restricted to only checking root-level keys
                if event == 'map_key' and prefix == '':
                    keys_found.add(value)

        if keys_found != self.fields:
            raise ValidationError('Expected the following fields: %s, found '
                                  '%s.' % (sorted(self.fields),
                                           sorted(keys_found)))


PlacementsDirFmt = model.SingleFileDirectoryFormat(
    'PlacementsDirFmt', 'placements.json', PlacementsFormat)


# TODO: Format tests
class RAxMLinfoFormat(model.TextFileFormat):
    # TODO https://github.com/smirarab/sepp/blob/master/sepp-package/buildref/
    # reformat-info.py
    def _validate_(self, level):
        pass


class SeppReferenceFormat(model.DirectoryFormat):
    alignment = model.File(r'aligned-dna-sequences.fasta',
                           format=AlignedDNAFASTAFormat)
    phylogeny = model.File(r'tree.nwk', format=NewickFormat)
    raxml_info = model.File(r'raxml-info.txt', format=RAxMLinfoFormat)

    def _validate_(self, level):
        seqs = self.alignment.view(skbio.TabularMSA)
        tree = self.phylogeny.view(skbio.TreeNode)

        seqs.reassign_index(minter='id')
        alignment_ids = set(seqs.index)
        phylogeny_ids = {t.name for t in tree.tips()}

        print(alignment_ids)
        print(phylogeny_ids)

        if alignment_ids != phylogeny_ids:
            raise ValidationError('IDs found in the alignment file that are '
                                  'missing in the phylogeny file: %s. IDs '
                                  'found in the phylogeny file that are '
                                  'missing in the alignment file: %s.'
                                  % (sorted(alignment_ids - phylogeny_ids),
                                     sorted(phylogeny_ids - alignment_ids)))
