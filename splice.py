import json
import random 
from lhotse import *
import os.path 
import numpy as np 
import sys 
supervisions=json.load(open('supervisions.json'))
recordings=json.load(open('recording_dict.json'))
def create_cs_audio(input_file_path,output_directory_path):
	generated_text=open(input_file_path,'r').readlines()
	#code_switched_sentence=generated_text[0]
	#sentence_token=code_switched_sentence.split() 
	random.seed(10)
	filename=input_file_path.split('/')[-1]
	length=len(generated_text) 
	for i in range(7,8):
		code_switched_sentence=generated_text[i]
		sentence_token=code_switched_sentence.split()
		cut=None
		energy_to_match=0.01
		for token in sentence_token:
			#token=json.dumps(token).strip('\"')
			print(token) 
			if(token in supervisions):
				matched_sups=supervisions[token]
				#random.shuffle(matched_sups)
				if(len(matched_sups)>50):
					random.shuffle(matched_sups)
					matched_sups=matched_sups[0:50]
				#print(len(matched_sups))
				sups_recs=[(SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0]), Recording.from_file(recordings[sup[1]][0]),recordings[sup[1]][1]) for sup in matched_sups] 
				#print('here1') 
				cut_set=[(MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup]),energy) for(sup,recording,energy) in sups_recs]
				#print('here2')
				#audio_energy_difs=[abs(energy_to_match-energy) for (_,energy) in cut_set]
				#print(min(audio_energy_difs))
				#min_dif=min(audio_energy_difs)
				#min_index=binary_search(audio_energy_difs,min_dif)
				#min_index=audio_energy_difs.index(min(audio_energy_difs))
				
				def find_within_threshold(cut_set):
					min_index=0
					min_val=100
					for i in range(len(cut_set)): 
						if(abs(energy_to_match-cut_set[i][1])<=0.001):
							return i
						else: 
							if(min_val>=abs(energy_to_match-cut_set[i][1])):
								min_val=abs(energy_to_match-cut_set[i][1])
								min_index=i
						
					return min_index

				min_index=find_within_threshold(cut_set)

				if(not cut):
					cut=cut_set[min_index][0]

				else: 
					cut=cut.append(cut_set[min_index][0])
				#energy_to_match=cut_set[min_index][1]
				#cut=cut.extend_by(duration=0.05,direction='right')
				#cut=cut.pad(duration=cut.duration+0.05)
				#cuts.append(cut) 
	
				#print(len(matched_sups))
	
	
		cut.save_audio(output_directory_path+'/'+filename+'_line_'+str(i)+'.wav')

if __name__ == "__main__":
	create_cs_audio(sys.argv[1], sys.argv[2])

 

