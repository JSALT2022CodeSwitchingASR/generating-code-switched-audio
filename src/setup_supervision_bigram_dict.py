#!/usr/bin/env python3

# Copyright 2023 Jons Hopkins University (Amir Hussein)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import json
import sys
from utils import dump_pickled, load_pickled
import msgspec
from lhotse import Recording
from tqdm import tqdm

#create supervision segment dictionary and save it as 
# supervisions.pkl in output folder sup_dict_folder

def setup_sup_dict(ctm_file_path, recording_dict_path,sup_dict_folder):
	ctm_lines = open(ctm_file_path,'r').readlines()
	#recording_set=json.load(open(recording_dict_path))
	recording_set = msgspec.json.decode(load_pickled(recording_dict_path))
	supervision_segments={}
	loaded_recs = {}
	for i in tqdm(range(len(ctm_lines)-1), desc="Converting CTM tokens to supervisions", ncols=100, ascii=True):
		#print(i)
		line_1 = ctm_lines[i].strip().split()
		line_2 = ctm_lines[i+1].strip().split()

		recording_id_1 = line_1[0]
		recording_id_2 = line_2[0]

		if(recording_id_1 == recording_id_2):
			token_1 = line_1[4]
			text_1 = line_1[4]
			channel_1 = line_1[1]
			start_1 = float(line_1[2])
			duration_1 = float(line_1[3])
			
			token_2 = line_2[4]
			text_2 = line_2[4]
			channel_2 = line_2[1]
			start_2 = float(line_2[2]) 
			duration_2 = float(line_2[3])

			bi_start = start_1
			gap = start_2 - (start_1 + duration_1)
			if( gap >= 0 and gap < 0.5 ):
				bi_duration = duration_1 + gap + duration_2
				bi_token = token_1 + ' ' + token_2
				bi_channel = channel_1
				bi_text = text_1 + ' ' + text_2
			
				if(recording_id_1 in recording_set):
					if recording_id_1 not in loaded_recs:
						rec = Recording.from_file(recording_set[recording_id_1])
						loaded_recs[recording_id_1] = rec

					elif recording_id_1 in loaded_recs:
						rec = loaded_recs[recording_id_1]

					new_start = max(0.0, bi_start-0.05) 
					end = bi_start + bi_duration 
					new_end = min(end + 0.05, rec.duration) 
					new_duration = new_end-new_start
					if(bi_token in supervision_segments):
						#sup=(bi_token,recording_id_1, bi_start, bi_duration, bi_channel, bi_text)
						sup = (str(i).zfill(8),recording_id_1, new_start, new_duration, bi_channel, bi_text)
						supervision_segments[bi_token].append(sup)
					else:
						#sup=(bi_token,recording_id_1, bi_start, bi_duration, bi_channel, bi_text)
						sup = (str(i).zfill(8),recording_id_1, new_start, new_duration, bi_channel, bi_text)
						supervision_segments[bi_token]=[sup]

	out_file = sup_dict_folder+"/bigram_supervisions.pkl"
	dump_pickled(msgspec.json.encode(supervision_segments), out_file)
	# out_file = open(sup_dict_folder+"/bigram_supervisions.json", "w")
	# json.dump(supervision_segments, out_file)

if __name__ == "__main__":
	setup_sup_dict(sys.argv[1], sys.argv[2], sys.argv[3])
