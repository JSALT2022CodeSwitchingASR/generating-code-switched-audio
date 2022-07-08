import json 
import os
from lhotse import * 
recording_file=open('/jsalt1/exp/wp2/audio_cs_aug/exp1/align/wav.scp','r') 

lines=recording_file.readlines() 
i=0
recordings={}
for line in lines:
	print(i) 
	line=line.split() 
	if(len(line)>2):
		#print(line[-2])
		if(os.path.isfile(line[-2])):
			#recording=Recording.from_file(line[-2])
			energy=audio.audio_energy(audio.AudioSource(type='file',channels=[0],source=line[-2]).load_audio())
			recordings[line[0]]=(line[-2], energy)
			
		else: 
			print(line[-2])
	else:
		if(os.path.isfile(line[1])):
			energy=audio.audio_energy(audio.AudioSource(type='file',channels=[0],source=line[1]).load_audio())			
			recordings[line[0]]=(line[1],energy)
		else: 
			print(line[1]) 
	i+=1
print(len(recordings))
#recs=RecordingSet.from_recordings(recordings) 
#recs.to_file('recordings.jsonl')
f=open('recording_dict.json', 'w') 
json.dump(recordings,f)
