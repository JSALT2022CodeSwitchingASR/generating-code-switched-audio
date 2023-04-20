#!/usr/bin/env python3

# Copyright 2023 Johns Hopkins University (Amir Hussein)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)


import pickle
import logging
import os

def dump_pickled(data, path):
    logging.info(f"Dumping pickled data: {os.path.basename(path)}")
    with open(path, 'wb') as file:
        pickle.dump(data, file)

def load_pickled(path):
    logging.info(f"Loading pickled data: {os.path.basename(path)}")
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data

