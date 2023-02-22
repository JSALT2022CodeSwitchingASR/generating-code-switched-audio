steps to generate audio 

1) with wav.scp file for the monolingual utterances, generate a recording dictionary 
using setup_recording_dict.py in speechCollage/src2 
usage is: python setup_recording_dict.py wav_scp_path output_folder 
	e.g. python setup_recording_dict.py home/wav.scp output (do not include / in output path) 

2) with ctm file for the monolingual utterances and recording dictionary, create a supervision 
dictionary. For randomly generated utterances with unigrams and no signal processing, 
use src2/setup_supervision_dict.py. To create a supervision dictionary for unigrams with signal processing, 
use src2/setup_supervision_improved_dict.py 
usage: python setup_supervision_dict.py ctm_file_path rec_dict_path output 
eg. python setup_supervision_dict.py home/ctm.mono home/recordings.json output (do not include / in output path)

3) modify either sbatch_unigram.sh (generates randomly) or sbatch_unigram_improved.sh (random with signal processing) 
with the desired paths to the dictionaries and the input text and output directory. Make sure that the first 
word in each line of the text is an utterance ID. 
Example: 01NC01FBX_0101-1013706-1015417 then exam 怎 么 办 

4) run the generation with sbatch -p RM-shared --cpus-per-task 32 <script> 

5) once the audios are generated (will take 8-9 hours for 50 hours), create wav.scp file by 
make_wav_scp.py. Must modify the paths within that file.  

6) create utt2spk and spk2utt file with make_utt2spk.py. Again, must modify the paths in that file.  

7) use the wav.scp, utt2spk, spk2utt and generated transcripts.txt in the generated audio folder 
for espnet training 

8) I usually run the stage 2-4 on the generated audio, then combine this data with the monolingual speed perturbed 
(cat mono_wav.scp synth_wav.scp > mixed_wav.scp)(same thing for text, utt2spk and spk2utt) 

9) train using the train_asr_conformer.yaml and decode with decode_asr.yaml 




