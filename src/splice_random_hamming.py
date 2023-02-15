#!/usr/bin/env python3
# Copyright (c) Dorsa Z

# Apache 2.0


import json
import random
from lhotse import *
import torchaudio 
from torchaudio import * 
import torch 
import os.path
import numpy as np
import sys
from datetime import datetime

random.seed(10)
from lhotse.augmentation.transform import AudioTransform
from dataclasses import dataclass, field
import numpy as np
import torch
from lhotse.utils import (
    Seconds,
    compute_num_samples,
    during_docs_build,
    perturb_num_samples,
    fastcopy,
)
from typing import Callable, Dict, List, Optional, Tuple, Union

@dataclass
class Hamming(AudioTransform):
    """
    Hamming window
    """

    def __call__(self, samples: np.ndarray) -> np.ndarray:
        if isinstance(samples, np.ndarray):
            samples = torch.from_numpy(samples)
        augmented = samples*np.float32(np.hamming(len(samples)))
        return augmented.numpy()
def add_overlap(sample1, sample2, overlap=int(16000*0.12)):
    fn = Hamming()
    sample1 = fn(sample1)
    sample2 = fn(sample2)
    new = np.zeros(len(sample1)+len(sample2),dtype='float32')
    new[0:len(sample1)] = sample1
    new[len(sample1)-overlap:len(sample1)-overlap+len(sample2)]+= sample2
    return new

def load_dicts_modified(sup_dict_path, rec_dict_path):
    supervisions = json.load(open(sup_dict_path))
    recordings = json.load(open(rec_dict_path))
    return supervisions, recordings


def take_random(token,sups,recordings):
     matched_sups = sups[token]
     sup = random.sample(matched_sups, 1)[0]
     recording = recordings[sup[1]]
     sup = SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0,
                                     text=sup[0])
     c = MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,
                        supervisions=[sup])
     return c       
def create_cs_audio(generated_text, output_directory_path, supervisions, recordings): 
    length = len(generated_text)
    transcripts=[]
    alignments={}
    for i in range(length):
        line = generated_text[i].split()
        file_name = line[0]

        start_time = datetime.now()
        transcript=file_name + ' '
        alignment=[]
        sentence_token = line[1:]
        audio = None 
        index = 0 
        for j in range(len(sentence_token)):
            token = sentence_token[j]
            if (token in supervisions):
                transcript += (token+ ' ')
                if index ==0: 
                    c=take_random(token,supervisions,recordings)
                    c = c.perturb_volume(factor=5.)
                    audio=c.load_audio().squeeze()
                    audio = np.pad(audio, (0, int(0.05*16000)), 'constant') # padding 0.05s with zeros from both sides
                
                    index+=1 
                else:
                    c=take_random(token,supervisions,recordings)
                    c = c.perturb_volume(factor=5.) #increasing volume because it was too quiet 
                
                    #audio=np.append(audio,np.zeros((int(16000*0.01)),dtype='float32')) #the small pause 
                    if (len(audio) < int(16000*0.1)): #if segment is too short for overlap of 0.1 secs 
                        #audio = np.append(audio,np.zeros((int(16000*0.05)-len(audio)),dtype='float32'))
                        continue
                    audio2 = c.load_audio().squeeze()
                    audio2 = np.pad(audio2, (int(0.05*16000), int(0.05*16000)), 'constant') # padding 0.05s with zeros from both sides
                    audio = add_overlap(audio,audio2)
                    index+=1 

                 

        end_time = datetime.now()
        delta = (end_time - start_time)
        print('making sentence time: ', delta)

        start_time = datetime.now()
        if(index!=0):
            transcripts.append(transcript.strip())
            torchaudio.save(output_directory_path+'/'+file_name+'.wav', torch.from_numpy(np.expand_dims(audio,0)),sample_rate=16000, encoding="PCM_S", bits_per_sample=16)
        end_time = datetime.now()
        delta = (end_time - start_time)

        print('saving audio time: ', delta)

    with open(output_directory_path+'/transcripts.txt','a') as f: #in case there is oov, must use this transcripts as text for training
        for t in transcripts:
            f.write(t+'\n')
 


if __name__ == "__main__":
    sup_dict_path = sys.argv[1]
    rec_dict_path = sys.argv[2]
    #bins_dict_path = sys.argv[3]
    # non_freq_dict_path = sys.argv[3]i
    # sup_bin_1_dict_path = sys.argv[4]
    # sup_bin_2_dict_path = sys.argv[5]
    # sup_bin_3_dict_path = sys.argv[6]
    # sup_bin_4_dict_path = sys.argv[7]
    # sup_bin_5_dict_path = sys.argv[8]

    input_path = sys.argv[3]
    output_path = sys.argv[4]

    supervisions, recordings= load_dicts_modified(sup_dict_path, rec_dict_path)
        # non_freq_dict_path, sup_bin_1_dict_path, sup_bin_2_dict_path, sup_bin_3_dict_path,
        # sup_bin_4_dict_path, sup_bin_5_dict_path)
    generated_text = open(input_path, 'r').readlines()
    create_cs_audio(generated_text, output_path, supervisions, recordings)
