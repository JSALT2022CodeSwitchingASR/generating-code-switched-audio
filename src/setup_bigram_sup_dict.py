import json
import sys

#create supervision segment dictionary and save it as 
# supervisions.json in output folder sup_dict_folder

def setup_sup_dict(ctm_file_path, recording_dict_path,sup_dict_folder):
	ctm_file=open(ctm_file_path,'r')
	recording_set=json.load(open(recording_dict_path))
	lines=ctm_file.readlines()
	supervision_segments={}
	for i in range(0,len(lines)-1):
		#print(i)
		line_1=lines[i].split()
		line_2=lines[i+1].split()

		recording_id_1=line_1[0]
		recording_id_2=line_2[0]

		if(recording_id_1==recording_id_2):
			eyedee_1=line_1[4]
			text_1=line_1[4]
			channel_1=line_1[1]
			start_1=float(line_1[2])
	
			duration_1=float(line_1[3])
			
			eyedee_2=line_2[4]
			text_2=line_2[4]
			channel_2=line_2[1]
			start_2=float(line_2[2])
                
			duration_2=float(line_2[3])
			bi_start=start_1
			gap=start_2-(start_1+duration_1)
			if(gap>=0 and gap<0.5):
			
				
				bi_duration=duration_1+gap+duration_2
				bi_eyedee=eyedee_1+' ' + eyedee_2
				bi_channel=channel_1
				bi_text=text_1 + ' ' + text_2
			

				if(recording_id_1 in recording_set):
				
					if(bi_eyedee in supervision_segments):

						sup=(bi_eyedee,recording_id_1, bi_start, bi_duration,bi_channel, bi_text)
						supervision_segments[bi_eyedee].append(sup)
					else:
						sup=(bi_eyedee,recording_id_1, bi_start,bi_duration,bi_channel,bi_text)
						supervision_segments[bi_eyedee]=[sup]

	out_file = open(sup_dict_folder+"/bigram_supervisions.json", "w")
	json.dump(supervision_segments, out_file)

if __name__ == "__main__":
	setup_sup_dict(sys.argv[1], sys.argv[2], sys.argv[3])
