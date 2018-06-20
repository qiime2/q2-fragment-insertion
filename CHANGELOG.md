# q2-fragment-insertion changelog

## Version 2018.6.0 (changes since 0.1.0 go here)

* added function `filter-features` which takes a feature-table and a phylogeny and filters the table down to those features also included in the phylogeny. This becomes a standard tasks, since e.g. Deblur produces fragments that do not get inserted into the reference phylogeny by SEPP, but those features would cause errors in downstream diversity computation. Also see [QIIME2 forum discussion](https://forum.qiime2.org/t/filter-feature-table-phylogenetically/4462)

* adopted to QIIME2 version numbers.

* added `--debug` option, which together with `--verbose` will allow inspection of additional information of a SEPP run for further debugging. See [QIIME2 forum discussion](https://forum.qiime2.org/t/pass-verbose-flag-to-executable/4461)

* check fragment names: Siavash updated his SEPP code such that it will raise a ValueError if names of input fragments and names of reference sequences collide. Users can see this error when raising `--verbose` and `--debug` flag for `qiime fragment-insertion sepp`. See (https://github.com/smirarab/sepp/issues/33)
