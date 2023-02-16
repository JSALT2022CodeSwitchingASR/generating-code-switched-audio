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
from langdetect import detect
import sys 
from datetime import datetime
random.seed(50)
def load_dicts_modified(uni_sup_dict_path,bi_sup_dict_path, rec_dict_path):
    supervisions = json.load(open(uni_sup_dict_path))
    recordings = json.load(open(rec_dict_path))
    bi_sups = json.load(open(bi_sup_dict_path))
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
        seg=line[b:e+1]
        #print(seg)
        if(len(seg) ==1):
            segments.append(seg)
        elif(len(seg)==2):
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
    length=len(generated_text)
    transcripts=[]
    for i in range(length):
        line=generated_text[i].split()
        print(line)
        filename=line[0]
        ranges=find_boundaries(line[1:])
        print(ranges)
        segments=create_segments(ranges,line[1:],uni_sups,bi_sups)
        print(segments)
        start_time=datetime.now()
        transcript=filename+' '
        cut=None
        for j in range(len(segments)):
            seg=segments[j]
            l=len(seg)
            seg=' '.join(seg)
            token=seg
            print(seg)
            if(l==1 and seg in uni_sups):
                if(not cut):
                    #print('here1')
                    c=take_random(seg,uni_sups,recordings)
                    cut=c
                        
                else:
                    c=take_random(seg,uni_sups,recordings)
                    print(cut)
                    cut = cut.append(c) 
                transcript+=(seg+ ' ')
            elif(l==2 and seg in bi_sups):
                if(not cut):
                    #print('here3'
                    c=take_random(seg,bi_sups,recordings)
                    cut=c
                else:
                    c=take_random(seg,bi_sups,recordings)
                    print(cut)
                    cut=cut.append(c)
                   
                transcript+=(seg+ ' ')
        end_time=datetime.now()
        delta = (end_time-start_time)
        print('making sentence time: ', delta)
        start_time=datetime.now()
        if(cut):
            #cut.save_audio(output_directory_path+'/bi_'+filename+'.wav')	
            transcripts.append(transcript.strip())
            #alignments[filename]=alignment
            torchaudio.save(output_directory_path+'/bi_'+filename+'.wav',torch.from_numpy(cut.load_audio()),sample_rate=16000, encoding="PCM_S", bits_per_sample=16)
        end_time=datetime.now()
        delta = (end_time-start_time)

        print('saving audio time: ', delta)

    with open(output_directory_path+'/bi_transcripts.txt','a') as f:
        for t in transcripts:
            f.write(t+'\n')
'''if __name__ == "__main__":
    rec_dict_path='/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/data/recording_dict.json'
    unigram_sups_path='/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/data/unigram_vocab.json'
    unigram_bins_path='/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/data/unigram_bins.json'
    bigram_sups_path='/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/data/bigram_vocab.json'
    bigram_bins_path='/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/data/bigram_bins.json'
    
    recordings,uni_sups,uni_bins,bi_sups,bi_bins,percents=load_dicts(rec_dict_path,unigram_sups_path,unigram_bins_path,bigram_sups_path,bigram_bins_path)
    print('here')
  
    output_directory_path='.'
    generated_text=open('/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/dummy_2.txt','r').readlines()[0:1]
    create_cs_audio(generated_text,output_directory_path,recordings,uni_sups,uni_bins,bi_sups,bi_bins,percents)'''

if __name__=="__main__":
    rec_dict_path=sys.argv[1]
    unigram_v_path=sys.argv[2]
    unigram_bins_path=sys.argv[3]
    bigram_v_path=sys.argv[4]
    bigram_bins_path=sys.argv[5]
     
    recordings,uni_sups,uni_bins,bi_sups,bi_bins,percents=load_dicts(rec_dict_path,unigram_v_path,unigram_bins_path,bigram_v_path,bigram_bins_path) 

    output_directory_path='.'
    generated_text=open('/jsalt1/exp/wp2/audio_cs_aug/exp1/speech_gen_wp/dummy_2.txt','r').readlines()[0:1]
    create_cs_audio(generated_text,output_directory_path,recordings,uni_sups,uni_bins,bi_sups,bi_bins,percents)
