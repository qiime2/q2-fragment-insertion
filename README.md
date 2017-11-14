## Installation

Once QIIME2 is [installed](https://docs.qiime2.org/2017.10/install/native/), and you activated your QIIME2 environment, it should be possible to install `q2-fragment-insertion` with:

    git clone https://github.com/biocore/q2-fragment-insertion.git
    cd q2-fragment-insertion
    python setup.py install
    qiime dev refresh-cache

You will need Java to run SEPP, and you may need to install it. How you do it is dependent on your operating system. If you're on OSX, you likely need to grab a legacy version of Java. Information can be found [here](https://support.apple.com/kb/dl1572?locale=en_US).

## Important

Default reference (phylogeny and matching alignment) is Greengenes 13_8 at 99%.
You can provide your own reference via optional inputs `--i-reference-alignment` and `--i-reference-phylogeny`. Make sure that every tip of the reference phylogeny has exactly one corresponding sequence in the reference alignment. Insertion taxonomic lineage information can be obtained from the provided reference phylogeny, by concatenating internal node labels along the path from the root to the inserted fragment. Only node labels are considerd which contain Greengenes like infixes with two underscores `_` `_`, indicating taxonomic labels. Your reference phylogeny might contain other internal node labels which are not taxonomic labels.

Sequences which are not at least 75% similar by sequence identity to any record in the tree to insert into are not inserted into the tree.

A fragment may be reasonable to insert into multiple locations. However, downstream methods such as UniFrac cannot currently handle placement distributions. As such, the placement with the highest likelihood is choosen.

## Files produced

The plugin will generate three files:
  1. A `Phylogeny[Rooted]` type: This is the tree with the sequences placed (which could be inserted), and are identified by their corresponding sequence IDs. You can directly use this tree for phylogenetic diversity computation like UniFrac or Faith's Phylogenetic Diversity.
  2. A `Placements` type: It is a JSON object which, for every input sequence, describes the different possible placements.
  3. And last a `FeatureData[Taxonomy]` type: This is a table that holds a taxonomic lineage string for every fragment inserted into the tree. The lineage is obtained by traversing the tree from the fragment tip towards the root and collecting all taxonomic labels in the reference tree along this path. Thus, taxonomy is only as good as provided reference phylogeny. Note, taxonomic labels are identified by containing two underscore characters `_` `_` as in Greengenes. **As of Nov 2017: We do NOT encourage the use of this file, since it has not been compared to existing taxonomic assignment methods. Particularly since the default reference tree is not inline with the reference taxonomy.
