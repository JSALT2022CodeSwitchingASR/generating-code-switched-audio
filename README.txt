steps to generate audio 

1) with wav.scp file for the monolingual utterances, generate a recording dictionary 
using setup_recording_dict.py in speechCollage/src 
usage is: python setup_recording_dict.py wav_scp_path output_folder 
	e.g. python setup_recording_dict.py home/wav.scp output (do not include / in output path) 

2) with ctm file for the monolingual utterances and recording dictionary, create a supervision 
dictionary with src/setup_supervision_dict.py 
usage: python setup_supervision_dict.py ctm_file_path rec_dict_path output 
eg. python setup_supervision_dict.py home/ctm.mono home/recordings.json output (do not include / in output path)

3) modify either sbatch_unigram_random.sh (generates randomly) or sbatch_unigram_random_hamming.sh (random with hamming window) 
with the desired paths to the dictionaries and the input text and output directory 

4) run the generation with sbatch -p RM-shared --cpus-per-task 32 <script> 

5) once the audios are generated (will take 2-3 hours), create wav.scp file by 
make_wav_scp.py 

6) create utt2spk and spk2utt file with make_utt2spk.py 

7) use the wav.scp, utt2spk, spk2utt and generated transcripts.txt in the generated audio folder 
for espnet training 

8) I usually run the stage 2-4 on the generated audio, then combine this data with the monolingual speed perturbed 
(cat mono_wav.scp synth_wav.scp > mixed_wav.scp)(same thing for text, utt2spk and spk2utt) 

9) train using the train_asr_conformer.yaml and decode with decode_asr.yaml 




