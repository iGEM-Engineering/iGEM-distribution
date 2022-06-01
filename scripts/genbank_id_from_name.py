"""This file supplies methods for patching GenBank files that contain one record with a
missing/corrupt accessions. The method renames the record in the file by using its file name
as the name and ID for the record."""

import os
import glob

from Bio import SeqIO


def rename_genbank_from_file_name(file):
    with open(file) as f_in:
        record = SeqIO.read(f_in, 'gb')
    record.id = os.path.basename(file).removesuffix('.gb')
    record.name = record.id
    print(f'Rewriting {file} to have identity {record.id}')
    with open(file, 'w') as f_out:
        SeqIO.write(record, f_out, 'gb')


def rename_all_genbank_from_file_name(directory):
    for file in glob.glob(f'{directory}/*.gb'):
        rename_genbank_from_file_name(file)
