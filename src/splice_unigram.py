#!/usr/bin/env python3

# Authors: Dorsa Z, Jons Hopkins University (Amir Hussein) 
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)


import json
import random
from lhotse import SupervisionSegment, MonoCut, audio
import torchaudio
from torchaudio import * 
import torch 
import os.path
import numpy as np
import sys
from datetime import datetime
from utils import load_pickled
import msgspec

random.seed(10)
def load_dicts_modified(sup_dict_path, rec_dict_path):
    supervisions =  msgspec.json.decode(load_pickled(sup_dict_path))
    recordings =  msgspec.json.decode(load_pickled(rec_dict_path))
    return supervisions, recordings

def take_random(token,sups,recordings):
     matched_sups = sups[token]
     sup = random.sample(matched_sups, 1)[0]
     recording=recordings[sup[1]]
     sup = SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0,
                                     text=sup[-1])
     c = MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,
                        supervisions=[sup])
     return c   
    
def create_cs_audio(generated_text, output_directory_path, supervisions, recordings): 
    length = len(generated_text)
    transcripts=[]
    #alignments={}
    for i in range(length):
        line = generated_text[i].split()
        file_name = line[0]

        start_time = datetime.now()
        transcript=file_name + ' '
        #alignment=[]
        sentence_token = line[1:]
        cut = None
        for j in range(len(sentence_token)):
            token = sentence_token[j]
            if (token in supervisions):
                transcript += (token+ ' ')
                if not cut: 
                    c=take_random(token,supervisions,recordings)
                    cut=c
                    #cut = cut.perturb_volume(5.) #increase volume bc too quiet 
                else:
                    c=take_random(token,supervisions,recordings)
                    #c = c.perturb_volume(5.)
                    cut=cut.append(c)
                   

                 

        end_time = datetime.now()
        delta = (end_time - start_time)
        # print('making sentence time: ', delta)

        start_time = datetime.now()
        if(cut):
            transcripts.append(transcript.strip())
            #alignments[file_name]=alignment
            torchaudio.save(output_directory_path+'/'+file_name+'.wav', torch.from_numpy(cut.load_audio()),sample_rate=16000, encoding="PCM_S", bits_per_sample=16)
        end_time = datetime.now()
        delta = (end_time - start_time)

        # print('saving audio time: ', delta)

    with open(output_directory_path+'/transcripts.txt','a') as f:
        for t in transcripts:
            f.write(t+'\n')
   
if __name__ == "__main__":
    sup_dict_path = sys.argv[1]
    rec_dict_path = sys.argv[2]

    input_path = sys.argv[3]
    output_path = sys.argv[4]

    supervisions, recordings= load_dicts_modified(sup_dict_path, rec_dict_path)
        # non_freq_dict_path, sup_bin_1_dict_path, sup_bin_2_dict_path, sup_bin_3_dict_path,
        # sup_bin_4_dict_path, sup_bin_5_dict_path)
    generated_text = open(input_path, 'r').readlines()
    create_cs_audio(generated_text, output_path, supervisions, recordings)
