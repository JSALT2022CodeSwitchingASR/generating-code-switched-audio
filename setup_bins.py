import json 
import numpy as np 

#split supervision dict into 5 bins based on energy + 
# a supervisions dict of non freq words


def load_dicts(supervisions_dict_path, recording_dict_path):
	sups=json.load(open(supervisions_dict_path))
	recs=json.load(open(recording_dict_path))
	return sups,recs

def create_non_freq_words_sups(supervisions_dict):

	sups=supervisions_dict
	non_freq_words=[]
	non_freq_word_sups={}
	for word in sups.keys(): 
		if(len(sups[word])<=10):
			non_freq_word_sups[word]=sups[word]
			non_freq_words.append(word)

	l=[sups.pop(word) for word in non_freq_words]
	return non_freq_word_sups,sups

def create_bins_by_percentile(recording_dict, supervisions_dict):

	energies=[]
	for rec in recording_dict.keys():
        	_,energy=recording_dict[rec]
        	energies.append(energy)

	percentiles=[0.0,25.0,50.0,75.0,100.0]

	np_arr=np.array(energies)
	percents=np.percentile(np_arr,percentiles)
	
	sups_bin_1={}
	sups_bin_2={} 
	sups_bin_3={}
	sups_bin_4={}
	sups_bin_5={}
	for word in supervisions_dict.keys(): 
		sups=supervisions_dict[word]
		sups_bin_1[word]=[]
		sups_bin_2[word]=[]
		sups_bin_3[word]=[]
		sups_bin_4[word]=[]
		sups_bin_5[word]=[]
		for sup in sups:
			energy=recording_dict[sup[1]][1]
			if(energy >= percents[0] and energy < percents[1]):
				sups_bin_1[word].append(sup)
			elif(energy >= percents[1] and energy < percents[2]):
				sups_bin_2[word].append(sup)
			elif(energy >= percents[2] and energy<percents[3]):
				sups_bin_3[word].append(sup)
			elif(energy >= percents[3] and energy < percents[4]):
				sups_bin_4[word].append(sup)
			else:
				sups_bin_5[word].append(sup)
		sups_bin_1[word].sort(key=lambda s:recording_dict[s[1]][1])
		sups_bin_2[word].sort(key=lambda s:recording_dict[s[1]][1])
		sups_bin_3[word].sort(key=lambda s:recording_dict[s[1]][1])
		sups_bin_4[word].sort(key=lambda s:recording_dict[s[1]][1])
		sups_bin_5[word].sort(key=lambda s:recording_dict[s[1]][1])
	
	return sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5
	

if __name__ == "__main__":
	sups,recs=load_dicts('/export/home/dzeinal/supervisions.json', '/export/home/dzeinal/recording_dict.json')
	non_freq_sups,sups_new=create_non_freq_words_sups(sups)
	sups_bin_1, sups_bin_2, sups_bin_3, sups_bin_4, sups_bin_5 = create_bins_by_percentile(recs, sups_new)
	
	out_file = open("non_freq_sups.json", "w")
	json.dump(non_freq_sups, out_file)	

	out_file = open("sups_bin_1.json","w")
	json.dump(sups_bin_1,out_file)

	out_file=open("sups_bin_2.json", "w")
	json.dump(sups_bin_2, out_file) 

	out_file=open("sups_bin_3.json", "w")
	json.dump(sups_bin_3,out_file)

	out_file=open("sups_bin_4.json", "w")
	json.dump(sups_bin_4, out_file)

	out_file=open("sups_bin_5.json","w")
	json.dump(sups_bin_5,out_file)


