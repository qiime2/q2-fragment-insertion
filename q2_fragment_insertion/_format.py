# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model


class PlacementsFormat(model.TextFileFormat):
    def sniff(self):
        line = open(str(self)).readline()

        # it's json... but would be very expensive to parse
        return line[0] == '{'


PlacementsDirFmt = model.SingleFileDirectoryFormat(
    'PlacementsDirFmt', 'placements.json', PlacementsFormat)


class RAxMLinfoFormat(model.TextFileFormat):
    def sniff(self):
        with open(str(self), 'r') as f:
            for line in f.readlines():
                # in Greengenes and Silva cases, file starts with a lot of
                # those warnings which we can use to "sniff" the file format
                if line.startswith('IMPORTANT WARNING: Sequences '):
                    return True
                # however, the more stable method is to watch out for the
                # following line, which should be included in all cases.
                elif line.startswith('RAxML was called as follows:'):
                    return True
        return False


RAxMLinfoDirFmt = model.SingleFileDirectoryFormat(
    'RAxMLinfoDirFmt', 'raxml_info.txt', RAxMLinfoFormat)
