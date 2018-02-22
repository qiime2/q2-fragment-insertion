# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model
import re


class PlacementsFormat(model.TextFileFormat):
    def sniff(self):
        line = open(str(self)).readline()

        # it's json... but would be very expensive to parse
        return line[0] == '{'


PlacementsDirFmt = model.SingleFileDirectoryFormat(
    'PlacementsDirFmt', 'placements.json', PlacementsFormat)


class RAxMLinfoFormat(model.TextFileFormat):
    def sniff(self):
        pplacer_pattern = '.* RAxML version ([^ ]+)'
        with open(str(self), 'r') as f:
            for line in f.readlines():
                # in Greengenes and Silva cases, file starts with a lot of
                # those warnings which we can use to "sniff" the file format
                if line.startswith('IMPORTANT WARNING: Sequences '):
                    return True
                # however, the more stable method is to watch out for the
                # following line, which should be included in all cases.
                # the regex is copy and pasted from pplacers code:
                # https://github.com/matsen/pplacer/blob/1189285ce98de64cfa8c
                # 4f121c3afc5d8d03893f/pplacer_src/parse_stats.ml#L64
                elif len(re.findall(pplacer_pattern, line)) > 0:
                    return True
        return False


RAxMLinfoDirFmt = model.SingleFileDirectoryFormat(
    'RAxMLinfoDirFmt', 'raxml_info.txt', RAxMLinfoFormat)
