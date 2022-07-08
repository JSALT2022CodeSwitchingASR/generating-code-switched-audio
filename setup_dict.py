from lhotse import SupervisionSegment,SupervisionSet,RecordingSet
import json
#create supervision segment dictionary 

ctm_file=open('/jsalt1/exp/wp2/audio_cs_aug/exp1/align/ctm','r') 
recording_set=json.load(open('recording_dict.json'))
supervision_segments={}
i=0
for line in ctm_file.readlines(): 
	print(i)
	line = line.strip().split() 
	recording_id=line[0]
	#print(recording_id) 
	eyedee=line[4] 
	text=line[4] 
	channel=line[1] 
	start=float(line[2]) 
	duration=float(line[3]) 
	
	if(recording_id in recording_set):
		#print('here')
		if(eyedee in supervision_segments):

			sup=(eyedee,recording_id, start, duration,channel, text) 
			supervision_segments[eyedee].append(sup)
		else: 
			sup=(eyedee,recording_id, start,duration,channel,text)
			supervision_segments[eyedee]=[sup]
	i+=1 

#sups=SupervisionSet(None)
#sups = SupervisionSet.from_segments(supervision_segments)
#sups=sups.filter(lambda s: s.recording_id in recording_set)
'''print(len(supervision_segments))
sups.to_file('supervisions.jsonl')'''
print(len(supervision_segments))
out_file = open("supervisions.json", "w")
json.dump(supervision_segments, out_file)
