#!/usr/bin/env python3

# Copyright 2023 Jons Hopkins University (Amir Hussein)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import json
import sys 
from utils import dump_pickled, load_pickled
import msgspec
import logging
from tqdm import tqdm

# create supervision segment dictionary and save it as 
# supervisions.json in output folder sup_dict_folder

def setup_sup_dict(ctm_file_path, recording_dict_path,sup_dict_folder):
	ctm_lines = open(ctm_file_path,'r').readlines() 
	recording_set = msgspec.json.decode(load_pickled(recording_dict_path))
	supervision_segments = {}
	loaded_recs = {}
	i = 0
	for j in tqdm(range(len(ctm_lines)), desc="Converting CTM tokens to supervisions", ncols=100, ascii=True):

		line = ctm_lines[j].strip().split() 
		recording_id = line[0]
		token = line[4] 
		text = line[4] 
		channel = line[1] 
		start = float(line[2]) 
		duration = float(line[3]) 

		if(recording_id in recording_set):

			if(token in supervision_segments):
					if(duration > 0.1):
							sup=(str(i).zfill(8),recording_id, start, duration,channel, text)
							supervision_segments[token].append(sup)
			else:
					if(duration > 0.1): 
							sup = (str(i).zfill(8),recording_id, start,duration,channel,text)
							supervision_segments[token]=[sup]
		else:
			logging.info(f"{recording_id} not in recordings_dict")
	
	out_file = sup_dict_folder+"/supervisions.pkl"
	logging.info(f"Dumping supervisions.pkl to {out_file}")
	dump_pickled(msgspec.json.encode(supervision_segments), out_file)
	# out_file = open(sup_dict_folder+"/supervisions.json", "w")
	# json.dump(supervision_segments, out_file)


	
if __name__ == "__main__": 
	setup_sup_dict(sys.argv[1], sys.argv[2], sys.argv[3])	 
