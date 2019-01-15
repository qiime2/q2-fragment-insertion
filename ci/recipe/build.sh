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

if [ "$(uname)" == "Darwin" ]; then
    rm -rf sepp-package/sepp/tools/bundled/Linux
fi

# we have an indent error in one of the sepp python source files, which gets fixed here
patch sepp-package/sepp/sepp/algorithm.py < indent.patch

# change DIR in SEPP wrapper to be relocatable
patch sepp-package/run-sepp.sh < reloc.patch
mkdir -p $PREFIX/share/
mv sepp-package $PREFIX/share/fragment-insertion

# configure SEPP
cd $PREFIX/share/fragment-insertion/sepp/ && python setup.py config -c ; cd -
# move SEPP binary into PREFIX/bin and update reference location
mkdir -p $PREFIX/bin/
mv $PREFIX/share/fragment-insertion/run-sepp.sh $PREFIX/bin
cp `cat $PREFIX/share/fragment-insertion/sepp/.sepp/main.config | grep "^path" -m 1 | cut -d "=" -f 2 | xargs dirname`/* $PREFIX/bin/

cp taxonomy_gg99.qza $PREFIX/share/fragment-insertion/ref/ && make install
