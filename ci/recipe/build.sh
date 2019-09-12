#!/bin/sh

set -e
set -x

# create share directory
mkdir -p $PREFIX/share/fragment-insertion/ref/

# create soft link for Greengenes 13.8 reference files
ln -s $PREFIX/share/sepp/ref/99_otu_taxonomy.txt $PREFIX/share/fragment-insertion/ref/
ln -s $PREFIX/share/sepp/ref/gg_13_5_ssu_align_99_pfiltered.fasta $PREFIX/share/fragment-insertion/ref/
ln -s $PREFIX/share/sepp/ref/RAxML_info-reference-gg-raxml-bl.info $PREFIX/share/fragment-insertion/ref/
ln -s $PREFIX/share/sepp/ref/reference-gg-raxml-bl-rooted-relabelled.tre $PREFIX/share/fragment-insertion/ref/

# convert non-default Silva reference into qiime2 artifacts
qiime tools import --type "Phylogeny[Rooted]"            --input-path $PREFIX/share/sepp/ref/reference-99_otus_aligned_masked1977.fasta-rooted.tre --output-path $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.tree.qza
qiime tools import --type "FeatureData[AlignedSequence]" --input-path $PREFIX/share/sepp/ref/99_otus_aligned_masked1977.fasta                      --output-path $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.msa.qza
qiime tools import --type "RAxMLinfoFormat"              --input-path $PREFIX/share/sepp/ref/RAxML_info.99_otus_aligned_masked1977.fasta           --output-path $PREFIX/share/fragment-insertion/ref/silva12.8_99otus_aligned_masked1977.info.qza

# move reference files into correct conda directory
cp taxonomy_gg99.qza $PREFIX/share/fragment-insertion/ref/
