import json
import random 
from lhotse import *
import os.path 
import numpy as np 
import sys 
from datetime import datetime
random.seed(10)
def load_dicts(sup_dict_path, rec_dict_path,non_freq_dict_path, sup_bin_1_dict_path,sup_bin_2_dict_path,sup_bin_3_dict_path, sup_bin_4_dict_path,sup_bin_5_dict_path):

	supervisions=json.load(open(sup_dict_path))
	recordings=json.load(open(rec_dict_path))
	non_freq_sups=json.load(open(non_freq_dict_path)) 
	sups_bin_1=json.load(open(sup_bin_1_dict_path)) 
	sups_bin_2=json.load(open(sup_bin_2_dict_path)) 
	sups_bin_3=json.load(open(sup_bin_3_dict_path)) 
	sups_bin_4=json.load(open(sup_bin_4_dict_path))
	sups_bin_5=json.load(open(sup_bin_5_dict_path))
	
	energies=[]
	for rec in recordings.keys():
        	_,energy=recordings[rec]
        	energies.append(energy)

	percentiles=[0.0,25.0,50.0,75.0,100.0]

	np_arr=np.array(energies)
	percents=np.percentile(np_arr,percentiles)
	return supervisions,recordings,non_freq_sups, sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5, percents
def find_bin(energy,percentiles):
	
	if(energy>=percentiles[0] and energy<percentiles[1]):
		return 1 
	elif(energy>=percentiles[1] and energy < percentiles[2]): 
		return 2 

	elif(energy >=percentiles[2] and energy < percentiles[3]):
		return 3 
	elif(energy >= percentiles[3] and energy<percentiles[4]):
		return 4 
	else: 
		return 5 
		 
	
def find_token(token,b,sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5,recordings):
	if(b==1):
		if(token in sups_bin_1):
			matched_sups=sups_bin_1[token]
			sup=random.sample(matched_sups,1)[0]
			energy_to_match=recordings[sup[1]][1]
			recording=Recording.from_file(recordings[sup[1]][0])
			sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
			c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
			return c, energy_to_match
		elif(token in sups_bin_2):
                        matched_sups=sups_bin_2[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c, energy_to_match
		elif(token in sups_bin_3):
                        matched_sups=sups_bin_3[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c, energy_to_match
		elif(token in sups_bin_4):
                        matched_sups=sups_bin_4[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c, energy_to_match	
	 
		elif(token in sups_bin_5):
                        matched_sups=sups_bin_5[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c, energy_to_match

	if(b==2):
		if(token in sups_bin_2):
			matched_sups=sups_bin_2[token]
			sup=random.sample(matched_sups,1)[0]
			energy_to_match=recordings[sup[1]][1]
			recording=Recording.from_file(recordings[sup[1]][0])
			sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
			c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
			return c,energy_to_match 
		elif(token in sups_bin_1):
                        matched_sups=sups_bin_1[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		elif(token in sups_bin_3):
                        matched_sups=sups_bin_3[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		elif(token in sups_bin_4):
                        matched_sups=sups_bin_4[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
	 
		elif(token in sups_bin_5):
                        matched_sups=sups_bin_5[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match

	if(b==3):
		if(token in sups_bin_3):
			matched_sups=sups_bin_3[token]
			sup=random.sample(matched_sups,1)[0]
			energy_to_match=recordings[sup[1]][1]
			recording=Recording.from_file(recordings[sup[1]][0])
			sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
			c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
			return c,energy_to_match
		elif(token in sups_bin_2):
                        matched_sups=sups_bin_2[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		
		elif(token in sups_bin_4):
                        matched_sups=sups_bin_4[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		elif(token in sups_bin_1):
                        matched_sups=sups_bin_1[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
	 
		elif(token in sups_bin_5):
                        matched_sups=sups_bin_5[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match

	if(b==4):
		if(token in sups_bin_4):
			matched_sups=sups_bin_4[token]
			sup=random.sample(matched_sups,1)[0]
			energy_to_match=recordings[sup[1]][1]
			recording=Recording.from_file(recordings[sup[1]][0])
			sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
			c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
			return c,energy_to_match
		elif(token in sups_bin_3):
                        matched_sups=sups_bin_3[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		
		elif(token in sups_bin_5):
                        matched_sups=sups_bin_5[token]
                        sup=matched_sups[0]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match


		elif(token in sups_bin_2):
                        matched_sups=sups_bin_2[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		elif(token in sups_bin_1):
                        matched_sups=sups_bin_1[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
	 


	if(b==5):
		if(token in sups_bin_5):
			matched_sups=sups_bin_5[token]
			sup=random.sample(matched_sups,1)[0]
			energy_to_match=recordings[sup[1]][1]
			recording=Recording.from_file(recordings[sup[1]][0])
			sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
			c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
			return c,energy_to_match
		elif(token in sups_bin_4):
                        matched_sups=sups_bin_4[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		
		elif(token in sups_bin_3):
                        matched_sups=sups_bin_3[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match


		elif(token in sups_bin_2):
                        matched_sups=sups_bin_2[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
		elif(token in sups_bin_1):
                        matched_sups=sups_bin_1[token]
                        sup=matched_sups[-1]
                        energy_to_match=recordings[sup[1]][1]
                        recording=Recording.from_file(recordings[sup[1]][0])
                        sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                        c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
                        return c,energy_to_match
	 



def create_cs_audio(input_file_path,output_directory_path,supervisions, recordings,sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5, percents):
	generated_text=open(input_file_path,'r').readlines()
	
	filename=input_file_path.split('/')[-1]
	length=len(generated_text) 
	for i in range(length):
		start_time=datetime.now()
		code_switched_sentence=generated_text[i]
		sentence_token=code_switched_sentence.split()
		cut=None
		energy_to_match=0.0
		for j in range(len(sentence_token)):
			token=sentence_token[j]
			print(token) 
			if(token in supervisions):
				if(j==0):
					matched_sups=supervisions[token]
					#print(matched_sups)
					sup=random.sample(matched_sups,1)[0]
					#print(sup)
					#print(recordings[sup[1]])
					energy_to_match=recordings[sup[1]][1]
					recording=Recording.from_file(recordings[sup[1]][0])
					sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
						
					cut=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])		
	
				else:
					if(token in non_freq_sups):
						matched_sups=non_freq_sups[token]
						sup=random.sample(matched_sups,1)[0]
						energy_to_match=recordings[sup[1]][1]
						recording=Recording.from_file(recordings[sup[1]][0])
						sup=SupervisionSegment(id=sup[0], recording_id=sup[1], start=sup[2], duration=sup[3], channel=0, text=sup[0])
                                                
						c=MonoCut(id=sup.id, start=sup.start, duration=sup.duration, channel=sup.channel, recording=recording,supervisions=[sup])
						cut=cut.append(c)
					else:
						b=find_bin(energy_to_match,percents)
						c,e=find_token(token,b,sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5,recordings)
						cut=cut.append(c)
						energy_to_match=e
		end_time=datetime.now()
		delta = (end_time-start_time)
		print('making sentence time: ', delta)

		start_time=datetime.now() 
		cut.save_audio(output_directory_path+'/farasa_ec_spf_28_09_2021_'+str(i)+'.wav')
		end_time=datetime.now() 
		delta = (end_time-start_time)

		print('saving audio time: ', delta)
if __name__ == "__main__":
	sup_path=sys.argv[1] 
	rec_path=sys.argv[2] 
	non_freq_dict_path=sys.argv[3]
	sup_bin_1_dict_path=sys.argv[4]
	sup_bin_2_dict_path=sys.argv[5]
	sup_bin_3_dict_path=sys.argv[6]
	sup_bin_4_dict_path=sys.argv[7]
	sup_bin_5_dict_path=sys.argv[8]

	input_path=sys.argv[9]
	output_path=sys.argv[10] 

	supervisions,recordings,non_freq_sups, sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5, percents = load_dicts(sup_dict_path, rec_dict_path,non_freq_dict_path, sup_bin_1_dict_path,sup_bin_2_dict_path,sup_bin_3_dict_path, sup_bin_4_dict_path,sup_bin_5_dict_path)
	create_cs_audio(input_path, output_path, supervisions, recordings,non_freq_sups, sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5, percents)

 

