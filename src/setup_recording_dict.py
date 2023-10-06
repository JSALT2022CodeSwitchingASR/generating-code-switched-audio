import json 
import os
import sys
import msgspec
from lhotse import Recording, RecordingSet
import logging
from tqdm import tqdm
from utils import dump_pickled

#setup recording dictionary give wave.scp file and 
#save it as recording_dict.json in rec_output_folder

def setup_rec_dict(wav_scp_path, rec_output_folder):

	recording_file = open(wav_scp_path, 'r') 

	lines = recording_file.readlines() 
	recordings = {}
	total_lines = len(lines)
	
	for i in tqdm(range(total_lines), desc="Processing recordings", ncols=100, ascii=True):
		line = lines[i].strip().strip('|')
		line = line.split() 	
		if(os.path.isfile(line[-1])):
			
			recordings[line[0]] = line[-1]
		else: 
			#log audio files that do not exist 
			print(f"Recording {line[-1]} does not exist")
	#recs = RecordingSet.from_recordings(Recording.from_file(p) for p in audio_paths)
	
	logging.info(f"Processed: {len(recordings)} / {total_lines}")
	out_file = rec_output_folder+'/recording_dict.pkl'
	#recs.to_file(rec_output_folder + "/recordings.jsonl.gz")
	logging.info(f"Dumping recordings_dict.pkl to {out_file} ")
	dump_pickled(msgspec.json.encode(recordings), out_file)


if __name__=="__main__":
	setup_rec_dict(sys.argv[1], sys.argv[2])
