import json
import sys 

#create supervision segment dictionary and save it as 
# supervisions.json in output folder sup_dict_folder

def setup_sup_dict(ctm_file_path, recording_dict_path,sup_dict_folder):
	ctm_file=open(ctm_file_path,'r') 
	recording_set=json.load(open(recording_dict_path))
	supervision_segments={}
	for line in ctm_file.readlines(): 
		print(1)
		line = line.strip().split() 
		recording_id=line[0]
		
		eyedee=line[4] 
		text=line[4] 
		channel=line[1] 
		start=float(line[2]) 
		duration=float(line[3]) 
	
		if(recording_id in recording_set):
			
			if(eyedee in supervision_segments):

				sup=(eyedee,recording_id, start, duration,channel, text) 
				supervision_segments[eyedee].append(sup)
			else: 
				sup=(eyedee,recording_id, start,duration,channel,text)
				supervision_segments[eyedee]=[sup]

	out_file = open(sup_dict_folder+"/supervisions.json", "w")
	json.dump(supervision_segments, out_file)

if __name__ == "__main__": 
	setup_sup_dict(sys.argv[1], sys.argv[2], sys.argv[3])	 
