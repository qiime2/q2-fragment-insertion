## Installation

Once QIIME2 is [installed](https://docs.qiime2.org/2017.10/install/native/), and you activated your QIIME2 environment, it should be possible to install `q2-fragment-insertion` with:

    conda install -c https://conda.anaconda.org/biocore q2-fragment-insertion
    qiime dev refresh-cache

## Important

Default reference (phylogeny and matching alignment) is Greengenes 13_8 at 99%.
You can provide your own reference via optional inputs `--i-reference-alignment` and `--i-reference-phylogeny`. Make sure that every tip of the reference phylogeny has exactly one corresponding sequence in the reference alignment. Insertion taxonomic lineage information can be obtained from the provided reference phylogeny, by concatenating internal node labels along the path from the root to the inserted fragment. Only node labels are considerd which contain Greengenes like infixes with two underscores `_` `_`, indicating taxonomic labels. Your reference phylogeny might contain other internal node labels which are not taxonomic labels.

Sequences which are not at least 75% similar by sequence identity to any record in the tree to insert into are not inserted into the tree.

A fragment may be reasonable to insert into multiple locations. However, downstream methods such as UniFrac cannot currently handle placement distributions. As such, the placement with the highest likelihood is choosen.

## Files produced

The plugin will generate two files:
  1. A `Phylogeny[Rooted]` type: This is the tree with the sequences placed (which could be inserted), and are identified by their corresponding sequence IDs. You can directly use this tree for phylogenetic diversity computation like UniFrac or Faith's Phylogenetic Diversity.
  2. A `Placements` type: It is a JSON object which, for every input sequence, describes the different possible placements.

## Example

QIIME 2's "Moving Pictures" [tutorial](https://docs.qiime2.org/2017.10/tutorials/moving-pictures/#generate-a-tree-for-phylogenetic-diversity-analyses) suggests constructing a de-novo phylogeny for the fragments, i.e `FeatureData[Sequence]`, to obtain a `Phylogeny[Rooted]` that can be used for phylogenetic diversity computation. "Fragment insertion" via this plugin provides an alternative way to acquire the `Phylogeny[Rooted]` by inserting sequences of `FeatureData[Sequence]` into a high quality reference phylogeny and thus provides multiple advantages over de-novo phylogenies, e.g. accurate branch lengths, multi-study meta-analyses, mixed region meta-analyses (e.g. V4 and V2).

Let us use the `FeatureData[Sequence]` from QIIME's tutorial as our input:

   - `rep-seqs.qza`: [view](https://view.qiime2.org/?src=https%3A%2F%2Fdocs.qiime2.org%2F2017.10%2Fdata%2Ftutorials%2Fmoving-pictures%2Frep-seqs.qza) | [download](https://docs.qiime2.org/2017.10/data/tutorials/moving-pictures/rep-seqs.qza)

The following single command will produce two outputs: 1) `phylogeny.qza` is the `Phylogeny[Rooted]` and 2) `placements.qza` provides placement distributions for the fragments (you will most likely ignore this output) (Computation might take some 10 minutes):
```
qiime fragment-insertion sepp-16s-greengenes \
  --i-representative-sequences rep-seqs.qza \
  --o-tree insertion-tree.qza \
  --o-placements insertion-placements.qza
```
Output artifacts:
   - `insertion-tree.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/blob/master/Example/insertion-tree.qza?raw=true)
   - `insertion-placements.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/blob/master/Example/insertion-placements.qza?raw=true)

You can then use `insertion-tree.qza` for all downstream analyses, e.g. "Alpha and beta diversity analysis", instead of `rooted-tree.qza`.

### Assign taxonomy

The *fragment-insertion* plugin provides two alternative methods to assign a taxonomic lineage to every fragment. Assume the tips of your reference phylogeny are e.g. OTU-IDs from Greengenes (which is the case when you use the default reference). If you have a taxonomic mapping for every OTU-ID to a lineage string, as provided by Greengenes, function `classify-otus` will detect the closest OTU-IDs for every fragment in the insertion tree and report this OTU-IDs lineage string for the fragment. Thus, the function expects two required input artifacts: 1) the representative-sequences of type `FeatureData[Sequence]` and 2) the resulting tree of a previous `sepp` run which is of type `Phylogeny[Rooted]`. For the example, we also specify a third, optional input [taxonomy_gg99.gza](https://raw.githubusercontent.com/biocore/q2-fragment-insertion/master/taxonomy_gg99.gza) of type `FeatureData[Taxonomy]`.

    qiime fragment-insertion classify-otus \
      --i-representative-sequences rep-seqs.qza \
      --i-tree insertion-tree.qza \
      --i-reference-taxonomy taxonomy_gg99.gza \
      --o-classification taxonomy.gza

Output artifacts:
   - `insertion-taxonomy.qza`: ~[view]()~ | [download](https://github.com/biocore/q2-fragment-insertion/blob/master/Example/insertion-taxonomy.qza?raw=true)

You need to make sure, that the `--i-reference-taxonomy` matches the reference phylogeny used with function `sepp`.

Alternatively, you can use the function `classify-paths` to a taxonomy. The lineage strings are obtained by traversing the insertion tree from each fragment tip towards the root and collecting all taxonomic labels in the reference tree along this path. Thus, taxonomy is only as good as provided reference phylogeny. Note, taxonomic labels are identified by containing two underscore characters `_` `_` as in Greengenes. **As of Nov 2017: We do NOT encourage the use of this function, since it has not been compared to existing taxonomic assignment methods. Particularly since the default reference tree is not inline with the reference taxonomy.**

### Import representative sequencs into QIIME 2 artifact

Assume you have a collection of representative sequences as a multiple fasta file, e.g. from downloading a `reference-hit.seqs.fa` Qiita file. You can *import* this file into a QIIME 2 artifact with the following command:

    qiime tools import \
    --input-path reference-hit.seqs.fa \
    --output-path reference-hit.seqs.qza \
    --type "FeatureData[Sequence]"    

The command will produce a new file with the name `reference-hit.seqs.qza`, which you can use as input `--i-representative-sequences` for the *fragment-insertion* plugin.

## Create conda packages (Developers only)

Obtain latest sources from this git repository:

    git clone https://github.com/biocore/q2-fragment-insertion.git

Move into newly cloned directory:

    cd q2-fragment-insertion

Execute the build command via a Makefile target:

    make conda

Upload the newly created conda package to biocore:

    anaconda upload -u biocore q2-fragment-insertion-0.1.0-py35h3e8d850_1.tar.bz2

Remember to do that for both, Linux and OSX.

## How to import taxonomy tables

    qiime tools import \
    --input-path taxonomy.tsv \
    --source-format HeaderlessTSVTaxonomyFormat \
    --type "FeatureData[Taxonomy]" \
    --output-path foo.gza
