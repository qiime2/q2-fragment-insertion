# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re

import ijson
import skbio

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

from q2_types.feature_data import AlignedDNAFASTAFormat
from q2_types.tree import NewickFormat


class PlacementsFormat(model.TextFileFormat):
    fields = {'tree', 'placements', 'metadata', 'version', 'fields'}

    def _validate_(self, level):
        # doi.org/10.1371/journal.pone.0031009
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


class RAxMLinfoFormat(model.TextFileFormat):
    def _validate_(self, level):
        sigs = ['This is RAxML version', 'Base frequencies',
                'Final GAMMA likelihood']

        info = self.path.read_text()

        for sig in sigs:
            new_sig = sig.replace(r' ', r'\W+')
            if not re.search(new_sig, info):
                raise ValidationError('Missing structured content: "%s".'
                                      % sig)


class SeppReferenceDirFmt(model.DirectoryFormat):
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

        if alignment_ids != phylogeny_ids:
            raise ValidationError('IDs found in the alignment file that are '
                                  'missing in the phylogeny file: %s. IDs '
                                  'found in the phylogeny file that are '
                                  'missing in the alignment file: %s.'
                                  % (sorted(alignment_ids - phylogeny_ids),
                                     sorted(phylogeny_ids - alignment_ids)))

        # NOTE: not worrying about validating raxml info file at present. In
        # the future we will have a method that will _run_ raxml as part of the
        # database construction process, which will guarantee that the tree
        # matches the raxml info file.
