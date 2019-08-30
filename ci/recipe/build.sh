#!/bin/sh

set -e
set -x

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
