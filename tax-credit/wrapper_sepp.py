#!/usr/bin/env python

import click
from os import makedirs
import os
from os.path import join
import tempfile
import sys
import multiprocessing
from shutil import rmtree
import pandas as pd
import subprocess

import qiime2
from qiime2.sdk import Artifact
import q2_fragment_insertion
from q2_types.feature_data import (AlignedDNASequencesDirectoryFormat,
                                   DNASequencesDirectoryFormat, DNAIterator,
                                   AlignedDNAIterator)
from q2_types.tree import NewickFormat, Phylogeny, Rooted
import skbio


def load_taxonomy(reference_taxonomy):
    if reference_taxonomy is not None:
        if str(reference_taxonomy).endswith('qza'):
            return Artifact.load(reference_taxonomy)
        else:
            return qiime2.Artifact.import_data(
                "FeatureData[Taxonomy]", reference_taxonomy)


def tax2tree(tmpdir, skbio_ref_tree, fp_taxonomy):
    """
    Re-decorate phylogeny with given taxonomy.

    Parameters
    ----------
    tmpdir : str
        Filepath to temporary working directory.
    skbio_ref_tree : skbio.TreeNode
        Input phylogenetic tree that shall be decorated.
    fp_taxonomy : str
        Filepath to taxonomy as two column tab separated table.

    Returns
    -------
    Qiime.Artifact(Phylogeny[Rooted]) : new decorated phylogeny.
    """
    # prepare inputs for tax2tree
    fp_phylogeny = join(tmpdir, 'phlyogeny.newick')
    skbio_ref_tree.write(fp_phylogeny)

    fp_tmp_taxonomy = join(tmpdir, 'taxonomy.tsv')
    load_taxonomy(fp_taxonomy).view(pd.DataFrame).to_csv(
        fp_tmp_taxonomy, sep="\t", header=False)

    fp_output_t2t = join(tmpdir, 'phylogeny_t2t.newick')
    print("Running tax2tree")
    with subprocess.Popen(
        "t2t decorate --consensus-map %s --tree %s --output %s --no-suffix" % (
         fp_tmp_taxonomy, fp_phylogeny, fp_output_t2t),
        shell=True,
        stdout=subprocess.PIPE) as env_present:
            if (env_present.wait() != 0):
                raise ValueError("Something went wrong")

    ar_output = qiime2.Artifact.import_data("Phylogeny[Rooted]", fp_output_t2t)
    return ar_output


@click.command()
@click.option('--method', type=click.Choice(['path', 'otus']), required=True)
@click.option('--cores', type=click.IntRange(1, multiprocessing.cpu_count(),
              clamp=True), required=False, default=1)
@click.option('--tmpdir', default=None, type=click.Path())
@click.argument('input_fragment_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
@click.option('--reference_alignment', type=click.Path(exists=True),
              required=True)
@click.option('--reference_phylogeny', type=click.Path(exists=True),
              required=True)
@click.option('--reference_info', type=click.Path(exists=True),
              required=False, default=None,
              help='raxml info file for references other than GG13.8')
@click.option('--reference_taxonomy', type=click.Path(exists=True),
              required=False, default=None,
              help='OTU to lineage tabular file')
# this is a dummy to allow tax-credit's framework to record reference name as
# a parameter
@click.option('--reference_name', default=None, required=False)
@click.option('--cross_validate', default=None, is_flag=True,
              help=('If set, sequence IDs provided in the input are first remo'
                    'ved from the given reference alignment/tree in order to p'
                    'erform a cross validation check, i.e. how well can inputs'
                    ' inserted into a reference where those inputs are unknown'
                    '.'))
@click.option('--novel_taxa_keep', default=None, type=click.Path(exists=True),
              required=False,
              help=('For tax-credit novel taxa analysis: fasta file that defin'
                    'es the set of sequences for the reference, i.e. all other'
                    's must be removed from reference.'))
def run_sepp(input_fragment_file, output_file, method, tmpdir, cores,
             reference_alignment, reference_phylogeny, reference_name,
             reference_info, reference_taxonomy, cross_validate,
             novel_taxa_keep):
    clear_tmpdir = False

    if tmpdir is None:
        tmpdir = tempfile.mkdtemp()
        clear_tmpdir = True
    if not os.path.exists(tmpdir):
        raise ValueError("Temporary working directory '%s' does not exists."
                         % tmpdir)
    sys.stderr.write("Using '%s' as temporary working directory.\n" % tmpdir)

    # load fragments into qiime2 artifact
    ar_repseq = qiime2.Artifact.import_data(
        'FeatureData[Sequence]', input_fragment_file)

    fp_insertion_tree = join(tmpdir, 'insertion_tree.qza')
    if not os.path.exists(fp_insertion_tree):
        # load reference alignment
        if str(reference_alignment).endswith('qza'):
            ar_ref_aln = Artifact.load(reference_alignment)
        else:
            ar_ref_aln = qiime2.Artifact.import_data(
                "FeatureData[AlignedSequence]", reference_alignment)

        # load reference phylogeny
        if str(reference_phylogeny).endswith('qza'):
            ar_ref_tree = Artifact.load(reference_phylogeny)
        else:
            ar_ref_tree = qiime2.Artifact.import_data(
                "Phylogeny[Rooted]", reference_phylogeny)

        ids_to_keep = None

        if cross_validate:
            ids_input = {seq.metadata['id']
                         for seq
                         in ar_repseq.view(DNAIterator)}
            ids_reference = {row.metadata['id']
                             for row
                             in ar_ref_aln.view(AlignedDNAIterator)}
            ids_missing = ids_input - ids_reference
            if len(ids_missing) > 0:
                sys.stderr.write(
                    ("Following %i input IDs could not be found in reference "
                     "and thus not removed from reference:\n%s\n") %
                    (len(ids_missing), "\n".join(ids_missing)))
            print("cross-validate: removing %i / %i sequences from reference."
                  % (len(ids_input & ids_reference), len(ids_reference)))
            ids_to_keep = ids_reference - ids_input

        if novel_taxa_keep is not None:
            # load trimmed reference sequences
            if str(novel_taxa_keep).endswith('qza'):
                ar_novel = Artifact.load(novel_taxa_keep)
            else:
                ar_novel = qiime2.Artifact.import_data(
                    "FeatureData[Sequence]", novel_taxa_keep)
            ids_to_keep = {seq.metadata['id']
                           for seq
                           in ar_novel.view(DNAIterator)}
            print("novel-taxa: reducing reference to %i sequences."
                  % (len(ids_to_keep)))

        if ids_to_keep is not None:
            # substract input seqs from reference alignment
            fp_crossval_alignment = join(
                tmpdir, 'cross-validate_reference_alignment.qza')
            if not os.path.exists(fp_crossval_alignment):
                skbio_ref_aln = ar_ref_aln.view(skbio.TabularMSA)
                skbio_ref_aln.index = [seq.metadata['id']
                                       for seq
                                       in skbio_ref_aln]
                skbio_ref_aln = skbio_ref_aln.loc[ids_to_keep]
                ar_ref_aln = qiime2.Artifact.import_data(
                    "FeatureData[AlignedSequence]", skbio_ref_aln)
                ar_ref_aln.save(fp_crossval_alignment)
            else:
                ar_ref_aln = Artifact.load(fp_crossval_alignment)

            fp_crossval_tree = join(
                tmpdir, 'cross-validate_reference_tree.qza')
            if not os.path.exists(fp_crossval_tree):
                skbio_ref_tree = ar_ref_tree.view(skbio.TreeNode)
                skbio_ref_tree = skbio_ref_tree.shear(ids_to_keep)
                # correct topology, i.e. merge one child internal nodes due to
                # tip removal
                skbio_ref_tree.prune()

                ar_ref_tree = tax2tree(
                    tmpdir, skbio_ref_tree, reference_taxonomy)
                ar_ref_tree.save(fp_crossval_tree)
            else:
                ar_ref_tree = Artifact.load(fp_crossval_tree)

        # run SEPP
        ar_tree, ar_placements = q2_fragment_insertion.sepp(
            ar_repseq.view(DNASequencesDirectoryFormat),
            threads=cores,
            reference_alignment=ar_ref_aln.view(
                AlignedDNASequencesDirectoryFormat),
            reference_phylogeny=ar_ref_tree.view(NewickFormat),
            # reference_info=reference_info
            )
        # save tree to file
        ar_tree = Artifact.import_data(Phylogeny[Rooted], ar_tree)
        ar_tree.save(fp_insertion_tree)
    else:
        ar_tree = Artifact.load(fp_insertion_tree)

    taxonomy = None
    if method == 'otus':
        ar_taxonomy = load_taxonomy(reference_taxonomy)

        # determine lineage for each rep-seq by finding closest OTU in
        # insertion-tree
        taxonomy = q2_fragment_insertion.classify_otus_experimental(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree.view(NewickFormat),
            ar_taxonomy.view(pd.DataFrame) if ar_taxonomy is not None else None)
    elif method == 'path':
        # determine lineage for each rep-seq by traversing from inserted tip
        # towards root
        # and collect taxonomic labels of reference tree
        taxonomy = q2_fragment_insertion.classify_paths(
            ar_repseq.view(DNASequencesDirectoryFormat),
            ar_tree.view(NewickFormat))

    # format results to match tax-credit
    taxonomy.index.name = '#OTU ID'
    taxonomy.rename(columns={'Taxon': 'taxonomy'}, inplace=True)
    taxonomy['confidence'] = 1.0
    taxonomy['num hits'] = 1

    # write results to file
    if os.path.dirname(output_file) != "":
        makedirs(os.path.dirname(output_file), exist_ok=True)
    taxonomy.to_csv(output_file, sep="\t")
    sys.stderr.write("Wrote results to '%s'.\n" % output_file)

    if clear_tmpdir:
        rmtree(tmpdir)


if __name__ == "__main__":
    run_sepp()
