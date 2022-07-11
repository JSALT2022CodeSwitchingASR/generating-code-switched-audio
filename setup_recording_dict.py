import json 
import os
from lhotse import * 
import sys
#setup recording dictionary give wave.scp file and 
#save it as recording_dict.json in rec_output_folder

def setup_rec_dict(wav_scp_path, rec_output_folder):

	recording_file=open(wav_scp_path, 'r') 

	lines=recording_file.readlines() 

	recordings={}
	for line in lines:
		line=line.split() 
		if(len(line)>2):
		
			if(os.path.isfile(line[-2])):
				
				energy=audio.audio_energy(audio.AudioSource(type='file',channels=[0],source=line[-2]).load_audio())
				recordings[line[0]]=(line[-2], energy)
			
			else: 
				#log audio files that do not exist 
				print(line[-2])
		else:
			if(os.path.isfile(line[1])):
				energy=audio.audio_energy(audio.AudioSource(type='file',channels=[0],source=line[1]).load_audio())			
				recordings[line[0]]=(line[1],energy)
			else: 
				#log audio files that do not exist
				print(line[1]) 

	f=open(rec_output_folder+'/recording_dict.json', 'w') 
	json.dump(recordings,f)


if __name__=="__main__":
	setup_rec_dict(sys.argv[1], sys.argv[2])
