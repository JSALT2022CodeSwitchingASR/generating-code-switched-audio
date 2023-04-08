import json
from itertools import groupby
from operator import itemgetter
import re
import random 
import torchaudio 
from torchaudio import * 
from lhotse import *
import torch 
import os.path 
import numpy as np 
import sys 
from dataclasses import dataclass, field
from lhotse.augmentation.transform import AudioTransform
from datetime import datetime
from utils import dump_pickled, load_pickled
import msgspec
import math 
import pdb
random.seed(50)

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

hamming = Hamming()

def add_overlap(sample1, sample2, overlap=int(16000*0.1)):

    sample2 = hamming(sample2)
    new = np.zeros(len(sample1)+len(sample2)-overlap,dtype='float32')
    new[0:len(sample1)] = sample1
    new[len(sample1)-overlap:len(sample1)-overlap+len(sample2)] += sample2
    return new

def load_dicts_modified(uni_sup_dict_path,bi_sup_dict_path, rec_dict_path):
    supervisions =  msgspec.json.decode(load_pickled(uni_sup_dict_path))
    recordings =  msgspec.json.decode(load_pickled(rec_dict_path))
    bi_sups =  msgspec.json.decode(load_pickled(bi_sup_dict_path))
    return supervisions,bi_sups, recordings

def take_random(token,sups,recordings):
     matched_sups = sups[token]
     sup = random.sample(matched_sups, 1)[0]
     recording = recordings[sup[1]]
     sup = SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0,
                                     text=sup[0])
     c = MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,
                        supervisions=[sup])
     return c

def isEnglishWord(word):
    # we use wordnet as well as enchant as wordnet check fails for contractions
    # and enchant check fails for british spelling
    # chinese character check 
    return re.sub(r'[\u4e00-\u9fff]+', '', word)==word and re.sub(r'[\u0600-\u06FF\s]+', '', word)==word

def find_boundaries(line):
    ranges={}
    ranges['en']=[]
    ranges['oth']=[]
    en_indices=[]
    oth_indices=[]
    for i in range(len(line)):
        word =line[i]
        if(isEnglishWord(word)):
            en_indices.append(i)
        else:
            oth_indices.append(i)

    for k, g in groupby(enumerate(en_indices), lambda ix : ix[0] - ix[1]):
        rangs=list(map(itemgetter(1), g))
        r=(rangs[0],rangs[-1])
        ranges['en'].append(r)
    for k, g in groupby(enumerate(oth_indices), lambda ix : ix[0] - ix[1]):
        rangs=list(map(itemgetter(1), g))
        r=(rangs[0],rangs[-1])
        ranges['oth'].append(r)
    r=ranges['en'] + ranges['oth']
    r.sort(key=lambda ix:ix[0])
    #print(r)
    return r

def create_segments(ranges, line,uni_v,bi_v):
    segments=[]
    for (b,e) in ranges:
        seg = line[b:e+1]
        #print(seg)
        if(len(seg) == 1):
            segments.append(seg)
        elif(len(seg) == 2):
            if(' '.join(seg) in bi_v):
                segments.append(seg)
            else:
                segments.append([seg[0]])
                segments.append([seg[1]])

        elif(len(seg)>=3):
            #length=len(seg)
            i=0
            while(i<len(seg)):
                ngram=random.randint(1,min(len(seg)-i,2))
                if(ngram==1):
                    sub_seg=seg[i:i+1]
                    #seg=seg[i+1:]
                    segments.append(sub_seg)
                    i+=1
                if(ngram==2):
                    sub_seg=seg[i:i+2]
                    #seg=seg[i+2:]
                    if(' '.join(sub_seg) in bi_v):
                        segments.append(sub_seg)
                    else:
                        segments.append([sub_seg[0]])
                        segments.append([sub_seg[1]])
                    i+=2
    return segments

def create_cs_audio(generated_text,output_directory_path,recordings,uni_sups,bi_sups):
    length = len(generated_text)
    transcripts = []
    for i in range(length):
        line = generated_text[i].split()
        #print(line)
        filename = line[0]
        #ranges = find_boundaries(line[1:])
        #print(ranges)
        #segments = create_segments(ranges,line[1:],uni_sups,bi_sups)
        #print(segments)
        start_time=datetime.now()
        transcript=filename+' '
        cut=None
        text = line[1:]
        j = 0
        while j < len(text): 
            token_uni = text[j]

            if j == len(text):
                token_bi = '<None>'
            else: 
                token_bi = ' '.join(text[j:j+2])
            
            # seg=' '.join(seg)
            # token=seg
            if(token_bi in bi_sups):
                if(cut is None):
                    #print('here3'
                    c=take_random(token_bi,bi_sups,recordings)
                    c_audio =c.load_audio().squeeze()
                    c_audio = c_audio/(math.sqrt(audio.audio_energy(c_audio)))
                    cut = hamming(c_audio)
                else:
                    c=take_random(token_bi,bi_sups,recordings)
                    c_audio = c.load_audio().squeeze()
                    c_audio = c_audio/math.sqrt(audio.audio_energy(c_audio))
                #    print(cut)
                    #cut=cut.append(c)
                    cut = add_overlap(cut,c_audio)
                j += 2
                transcript += (token_bi+ ' ')
            elif(token_uni in uni_sups):

                if(cut is None):
                    #print('here1')
                    c=take_random(token_uni,uni_sups,recordings)
                    c_audio =c.load_audio().squeeze()
                    c_audio = c_audio/(math.sqrt(audio.audio_energy(c_audio)))
                    cut = hamming(c_audio)
                        
                else:
                    c=take_random(token_uni,uni_sups,recordings)
                    #print(cut)
                    c_audio = c.load_audio().squeeze()
                    c_audio = c_audio/math.sqrt(audio.audio_energy(c_audio))
                #    print(cut)
                    #cut=cut.append(c)
                    cut = add_overlap(cut,c_audio)
                j += 1 
                transcript += (token_uni+ ' ')

            else:
                j += 1
        

        end_time=datetime.now()
        delta = (end_time-start_time)
        print('making sentence time: ', delta)
        start_time=datetime.now()
        if(cut is not None):
            #cut.save_audio(output_directory_path+'/bi_'+filename+'.wav')	
            transcripts.append(transcript.strip())
            #alignments[filename]=alignment
            torchaudio.save(output_directory_path+'/'+"bi_"+filename+'.wav', torch.from_numpy(np.expand_dims(cut,0)),sample_rate=16000, encoding="PCM_S", bits_per_sample=16)
        end_time=datetime.now()
        delta = (end_time-start_time)

        print('saving audio time: ', delta)

    with open(output_directory_path+'/bi_transcripts.txt','a') as f:
        for t in transcripts:
            f.write(t+'\n')