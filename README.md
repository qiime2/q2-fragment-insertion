## Installation

Once QIIME2 is [installed](https://docs.qiime2.org/2017.10/install/native/), it should be possible to install `q2-fragment-insertion` with:

    source activate qiime2-2017.10
    git clone https://github.com/wasade/q2-fragment-insertion.git
    cd q2-fragment-insertion
    python setup.py install
    qiime dev refresh-cache

You will need Java to run SEPP, and you may need to install it. How you do it is dependent on your operating system. If you're on OSX, you likely need to grab a legacy version of Java. Information can be found [here](https://support.apple.com/kb/dl1572?locale=en_US).

## Important

Currently only insertion into Greengenes 13_8 at 99% is available. We have not exposed mechanisms yet to construct references which can be used, however this can be accomplished by using [SEPP](https://github.com/smirarab/sepp) directly.

Sequences which are not at least 75% similar by sequence identity to any record in the tree to insert into are not inserted into the tree.

A fragment may be reasonable to insert into multiple locations. However, downstream methods such as UniFrac cannot currently handle placement distributions. As such, the placement with the highest likelihood is choosen.

## Files produced

The plugin will generate two files, one which is a `Phylogeny[Rooted]` type, and onc which is a `Placements` type. The former is the tree with the sequences placed (which could be inserted), and are identified by their corresponding sequence IDs. The latter is a JSON object which, for every input sequence, describes the different possible placements.

### Workaround for Q2 plugin error

You might encounter the following error when using the resulting `Phylogeny[Rooted]` tree artifact for ``qiime diversity beta-phylogenetic`` computations:
```
Plugin error from diversity:

  All non-root nodes in tree must have a branch length
```
The reason is one missing branch length for 'k__Bacteria'. Here is a quick and dirty fix:
  1. unpack the \*.qza archive, e.g. ``unzip foo.qza``
  2. find and edit file data/tree.nwk (It consists of only one but very long line)
  3. at the end of this one line, you will find the infix ``)'k__Bacteria')``
  4. change it into ``)'k__Bacteria':0.0)``, i.e. explicitly add the one missing branch length.
  5. recompress the \*.qza archive, e.g. ``zip -r foo.qza 041bb28d-9621-468c-93bd-a03f29f1f232/``
