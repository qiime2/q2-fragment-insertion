# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
from typing import List

from .plugin_setup import plugin
from ._format import PlacementsFormat, RAxMLinfoFormat


# TODO: tests


@plugin.register_transformer
def _1(data: dict) -> PlacementsFormat:
    ff = PlacementsFormat()
    with open(str(ff), 'w') as fp:
        fp.write(json.dumps(data))
    return ff


@plugin.register_transformer
def _2(ff: PlacementsFormat) -> dict:
    with ff.open() as fh:
        return json.load(fh)


@plugin.register_transformer
def _3(data: List[str]) -> RAxMLinfoFormat:
    ff = RAxMLinfoFormat()
    # TODO: pathlib
    with open(str(ff), 'w') as fp:
        for line in data:
            fp.write(line)
    return ff


@plugin.register_transformer
def _4(ff: RAxMLinfoFormat) -> List[str]:
    # TODO: pathlib
    with open(str(ff), 'r') as fp:
        return fp.readlines()
