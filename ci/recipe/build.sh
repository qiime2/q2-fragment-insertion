#!/bin/sh

set -e
set -x

# extract Greengenes 13.8 reference files
<<<<<<< HEAD
tar xjvf vendor/sepp-refs/gg/sepp-package.tar.bz sepp-package/ref/
rm -f sepp-package/ref/reference-gg-raxml-bl.tre
rm -f sepp-package/ref/reference-gg-raxml-bl-rooted.tre
=======
tar xjvf vendor/sepp-refs/gg/sepp-package.tar.bz sepp-package-gg/ref/

mkdir -p sepp-package/ref/
mv sepp-package-gg/ref/99_otu_taxonomy.txt                         sepp-package/ref/
mv sepp-package-gg/ref/gg_13_5_ssu_align_99_pfiltered.fasta        sepp-package/ref/
mv sepp-package-gg/ref/RAxML_info-reference-gg-raxml-bl.info       sepp-package/ref/
mv sepp-package-gg/ref/reference-gg-raxml-bl-rooted-relabelled.tre sepp-package/ref/
>>>>>>> 50b64428c7fad6a41e7b128b28b8830945ceb039

# extract Silva reference files
tar xjvf vendor/sepp-refs/silva/sepp-package-silva.tar.bz sepp-package-silva/ref/
tar xjvf vendor/sepp-refs/silva/sepp-package-silva-2.tar.bz sepp-package-silva/ref/

# convert non-default Silva reference into qiime2 artifacts
qiime tools import --type "Phylogeny[Rooted]"            --input-path sepp-package-silva/ref/reference-99_otus_aligned_masked1977.fasta-rooted.tre --output-path sepp-package/ref/silva12.8_99otus_aligned_masked1977.tree.qza
qiime tools import --type "FeatureData[AlignedSequence]" --input-path sepp-package-silva/ref/99_otus_aligned_masked1977.fasta                      --output-path sepp-package/ref/silva12.8_99otus_aligned_masked1977.msa.qza
# need to merge Silve PR first
# qiime tools import --type "RAxMLinfoFormat"              --input-path sepp-package-silva/ref/RAxML_info.99_otus_aligned_masked1977.fasta           --output-path sepp-package/ref/silva12.8_99otus_aligned_masked1977.info.qza

# move reference files into correct conda directory
mkdir -p $PREFIX/share/fragment-insertion/ref/
mv sepp-package/ref/ $PREFIX/share/fragment-insertion/ref/
cp taxonomy_gg99.qza $PREFIX/share/fragment-insertion/ref/

# clean up
rm -rf sepp-package-silva/ref/
