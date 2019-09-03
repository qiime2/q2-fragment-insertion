#!/bin/sh

set -e
set -x

# extract Greengenes 13.8 reference files
tar xjvf vendor/sepp-refs/gg/sepp-package.tar.bz sepp-package-gg/ref/

mkdir -p sepp-package/ref/
mv sepp-package-gg/ref/99_otu_taxonomy.txt                         sepp-package/ref/
mv sepp-package-gg/ref/gg_13_5_ssu_align_99_pfiltered.fasta        sepp-package/ref/
mv sepp-package-gg/ref/RAxML_info-reference-gg-raxml-bl.info       sepp-package/ref/
mv sepp-package-gg/ref/reference-gg-raxml-bl-rooted-relabelled.tre sepp-package/ref/

# extract Silva reference files
tar xjvf vendor/sepp-refs/silva/sepp-package-silva.tar.bz sepp-package-silva/ref/
tar xjvf vendor/sepp-refs/silva/sepp-package-silva-2.tar.bz sepp-package-silva/ref/
tar xjvf vendor/sepp-refs/gg/sepp-package.tar.bz sepp-package/

mv sepp-package-silva/ref/reference-99_otus_aligned_masked1977.fasta-rooted.tre sepp-package/ref/silva12.8_99otus_aligned_masked1977.tre
mv sepp-package-silva/ref/RAxML_info.99_otus_aligned_masked1977.fasta           sepp-package/ref/silva12.8_99otus_aligned_masked1977.info
mv sepp-package-silva/ref/99_otus_aligned_masked1977.fasta                      sepp-package/ref/silva12.8_99otus_aligned_masked1977.fasta

mkdir -p $PREFIX/share/fragment-insertion/ref/
mv sepp-package/ref/ $PREFIX/share/fragment-insertion/ref/
cp taxonomy_gg99.qza $PREFIX/share/fragment-insertion/ref/
