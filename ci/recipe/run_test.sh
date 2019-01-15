#!/bin/sh

set -x
set -e

# test if new Silva reference files are copied to the right location
ls $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.tre
ls $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.info
ls $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.fasta
