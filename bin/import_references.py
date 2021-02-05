# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import hashlib
import os
import os.path
import shutil
import sys
import urllib.request

import qiime2


def mkdir(fp):
    if not os.path.exists(fp):
        os.mkdir(fp)
    return fp


if __name__ == '__main__':
    GG = {
        'url': 'https://anaconda.org/bioconda/sepp-refgg138/4.3.6/download/'
               'noarch/sepp-refgg138-4.3.6-0.tar.bz2',
        'basename': 'gg',
        'md5sum': '2ed56bf7d9c1dbc98905b9812a8c53e8',
        'files': {
            'aligned-dna-sequences.fasta': 'share/sepp/ref/gg_13_5_ssu_align_'
                                           '99_pfiltered.fasta',
            'tree.nwk': 'share/sepp/ref/'
                        'reference-gg-raxml-bl-rooted-relabelled.tre',
            'raxml-info.txt': 'share/sepp/ref/'
                              'RAxML_info-reference-gg-raxml-bl.info',
        },
    }

    SILVA = {
        'url': 'https://anaconda.org/bioconda/sepp-refsilva128/4.3.6/download/'
               'noarch/sepp-refsilva128-4.3.6-0.tar.bz2',
        'basename': 'silva',
        'md5sum': '556e3f3092f20c3537b294d6fba581e8',
        'files': {
            'aligned-dna-sequences.fasta': 'share/sepp/ref/99_otus_aligned_'
                                           'masked1977.fasta',
            'tree.nwk': 'share/sepp/ref/reference-99_otus_aligned_masked1977'
                        '.fasta-rooted.tre',
            'raxml-info.txt': 'share/sepp/ref/'
                              'RAxML_info.99_otus_aligned_masked1977.fasta',
        },
    }

    out_dir = sys.argv[1]

    if not os.path.exists(out_dir):
        raise ValueError('please create output directory: %s' % (out_dir,))

    for db in [GG, SILVA]:
        # conda doesn't allow bot downloads, so build our own request to set UA
        req = urllib.request.Request(db['url'],
                                     headers={'User-Agent': 'Mozilla/5.0'})

        save_fp = os.path.join(out_dir, '%s.tar.gz' % (db['basename'],))

        if not os.path.exists(save_fp):
            with urllib.request.urlopen(req) as resp, \
                    open(save_fp, 'wb') as save_fh:
                shutil.copyfileobj(resp, save_fh)

        with open(save_fp, 'rb') as save_fh:
            hash_md5 = hashlib.md5()
            for chunk in iter(lambda: save_fh.read(4096), b""):
                hash_md5.update(chunk)
            md5sum = hash_md5.hexdigest()
            if md5sum != db['md5sum']:
                raise ValueError('invalid md5sum for %s: %s' %
                                 (db['basename'], md5sum))

        unpack_dir = mkdir(os.path.join(out_dir, db['basename']))
        shutil.unpack_archive(save_fp, unpack_dir)

        final_dir = mkdir(os.path.join(out_dir, '%s_out' % (db['basename'],)))
        for to_fp, from_fp in db['files'].items():
            final_fp = os.path.join(final_dir, to_fp)
            if not os.path.exists(final_fp):
                shutil.copyfile(os.path.join(out_dir, db['basename'], from_fp),
                                final_fp)

        db_qza = qiime2.Artifact.import_data('SeppReferenceDatabase',
                                             final_dir)
        db_qza.save('%s.qza' % (db['basename'],))
