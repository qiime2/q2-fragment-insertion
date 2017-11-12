## Installation

Once QIIME2 is [installed](https://docs.qiime2.org/2017.5/install/native/), it should be possible to install `q2-fragment-insertion` with:

    source activate qiime2-2017.5
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

The plugin will generate two files, one which is a `Phylogeny[Rooted]` type, and once which is a `Placements` type. The former is the tree with the sequences placed (which could be inserted), and are identified by their corresponding sequence IDs. The latter is a JSON object which, for every input sequence, describes the different possible placements. 

## Example

QIIME 2's "Moving Pictures" [tutorial](https://docs.qiime2.org/2017.10/tutorials/moving-pictures/#generate-a-tree-for-phylogenetic-diversity-analyses) suggests constructing a de-novo phylogeny for the fragments, i.e `FeatureData[Sequence]`, to obtain a `Phylogeny[Rooted]` that can be used for phylogenetic diversity computation. "Fragment insertion" via this plugin provides an alternative way to acquire the `Phylogeny[Rooted]` by inserting sequences of `FeatureData[Sequence]` into a high quality reference phylogeny and thus provides multiple advantages over de-novo phylogenies, e.g. accurate branch lengths, multi-study meta-analyses, mixed region meta-analyses (e.g. V4 and V2).

Let us use the `FeatureData[Sequence]` from QIIME's tutorial as our input:

   - `rep-seqs.qza`: [view](https://view.qiime2.org/?src=https%3A%2F%2Fdocs.qiime2.org%2F2017.10%2Fdata%2Ftutorials%2Fmoving-pictures%2Frep-seqs.qza) | [download](https://docs.qiime2.org/2017.10/data/tutorials/moving-pictures/rep-seqs.qza)

The following single command will produce three outputs: 1) `phylogeny.qza` is the `Phylogeny[Rooted]`, 2) `placements.qza` provides placement distributions for the fragments (you will most likely ignore this output) and 3) `classification.qza` which is a taxonomic classification for every fragment that has been inserted into the reference phylogeny and is of the type `FeatureData[Taxonomy]` (Computation might take some 10 minutes):
```
qiime fragment-insertion sepp-16s-greengenes \
  --i-representative-sequences rep-seqs.qzv \
  --o-tree insertion-tree.qza \
  --o-placements insertion-placements.qza \
  --o-classification insertion-taxonomy.qza
```
Output artifacts:
   - `insertion-tree.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/raw/readme_example/Example/insertion-tree.qza)
   - `insertion-placements.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/raw/readme_example/Example/insertion-placements.qza)
   - `insertion-taxonomy.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/raw/readme_example/Example/insertion-taxonomy.qza)
 
You can then use `insertion-tree.qza` for all downstream analyses, e.g. "Alpha and beta diversity analysis", instead of `rooted-tree.qza`.
