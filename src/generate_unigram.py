#!/usr/bin/env python3
# Copyright (c) SAC

# Apache 2.0



import os, sys
import multiprocessing
import time
import argparse
import splice_unigram as sp2
from lhotse import Recording
import logging
from pathlib import Path

parser = argparse.ArgumentParser(description='CS Audio generation pipeline')
# Datasets
parser.add_argument('--input', type=str, required=True,
                    help='Input text file including ..')
parser.add_argument('--output', type=str, required=True,
                    help='Output directory including ..')
parser.add_argument('--data', type=str, required=True, help='data path')
# Optimization options
parser.add_argument('--process', default=25, type=int, metavar='N',
                    help='number of multiprocess to run')

# parser.add_argument('--smoothing', action='store_true',
#                     help='use smoothing technique')


args = parser.parse_args()
print(args)


def generate(generated_text, output_directory_path, supervisions, recordings):
    sp2.create_cs_audio(generated_text, output_directory_path, supervisions, recordings)

def chunks(list, n):
    return [list[i:i+n] for i in range(0, len(list), n)]


def main():
    start_time = time.perf_counter()

    proc_count=args.process
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    data_path = Path(args.data)
    logging.info(f"Loading supervisions and recordings...")
    sup_path = data_path / 'supervisions.pkl'
    rec_path = data_path / 'recording_dict.pkl'

    supervisions, recordings= sp2.load_dicts_modified(sup_path, rec_path)
    #recordings = {key: (Recording.from_file(val).move_to_memory(channels=0,format="wav")) for key, val in recordings.items()}
    recordings = {key: Recording.from_file(val) for key, val in recordings.items()}
    logging.info(f"Finished loading supervisions and recordings...")

    inlist = open(args.input, 'r+', encoding='utf8', errors='ignore').readlines()
    #inlist=open(args.input,'r').readlines()
    outdir = args.output
    isExist = os.path.exists(outdir)
    if not isExist:
        os.makedirs(outdir)
    total = len(inlist)
    chunk_size = total // proc_count

    logging.info(f"Total: {total} Chunk size: {chunk_size}")

    slice = chunks(inlist, chunk_size)
    processes = []

    if proc_count <= 1:
        generate(inlist,outdir,supervisions,recordings)
    elif proc_count >= 2:
        for i, s in enumerate(slice):
            p = multiprocessing.Process(target=generate, args=(s,outdir, supervisions, recordings))
            p.start()
            processes.append(p)

    # Joins all the processes
    for p in processes:
        p.join()

    finish_time = time.perf_counter()

    logging.info(f"Program finished in {finish_time - start_time} seconds")


if __name__ == "__main__":
    main()
