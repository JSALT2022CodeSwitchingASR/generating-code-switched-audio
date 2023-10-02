#!/bin/bash 

# function to print logs
log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

stage=2
stop_stage=3
utils=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils
cmd=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils/parallel/slurm.pl
nj=150			# number of jobs across the nodes on cluster
mode=bigram 	# different modes to generate the code switching: unigram, unigram_imp, bigrams
dir=/jsalt2/amir/generating-code-switched-audio2/
logdir="$dir/slurm_log_${mode}"
indir="$dir/data"


if [ ! -d "$logdir" ]; then
  echo "$logdir does not exist, creating new $logdir"
  mkdir -p $logdir
fi

# input CS <text_file> 
input_text="${indir}/text_60K" 	
# desired output directory for audios 
outdir="$dir/exp/${mode}" 	

# directory to store json dictionaries of supervisions and recordings are stored
exp="$dir/data_${mode}" 	
if [ ! -d "$exp" ]; then
  echo "$exp does not exist, creating  $exp"
  mkdir -p $exp
fi

proc=1
clean_dir=false

if [ ${stage} -le -1 ] && [ ${stop_stage} -ge -1 ]; then
	if [ $clean_dir == true ]; then
		log "removing $outdir and $logdir"
		rm -rf $outdir
		rm -rf $logdir
	fi
	# split file to number of jobs
	log "Splitting $input_text into $nj jobs"

	split_scps=
	for n in $(seq $nj); do
		split_scps="$split_scps $logdir/out.$n"
	done

	$utils/split_scp.pl $input_text $split_scps

	mkdir -p $outdir
fi

# run array jobs 

if [ $mode == unigram ]; then 
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
		python src/setup_recording_dict.py ${indir}/wav.scp ${exp}

		log "Preparing supervisions: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
		python src/setup_supervision_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src/generate_unigram.py \
					--input $logdir/out.JOB \
					--output $logdir/gen_JOB \
					--data $exp \
					--process $proc
	fi

elif [ $mode == "unigram_imp" ]; then
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
		python src/setup_recording_dict.py ${indir}/wav.scp ${exp}

		log "Preparing supervisions with hamming window: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
		python src/setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src/generate_unigram_improved.py \
					--input $logdir/out.JOB \
					--output $logdir/gen_JOB \
					--data $exp \
					--process $proc
	fi
elif [ $mode == "bigram" ]; then
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
		python src/setup_recording_dict.py ${indir}/wav.scp ${exp}
		
		log "Preparing supervisions: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
		python src/setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
		
		log "Preparing bigram supervisions: python src/setup_bigram_sup_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
		python src/setup_bigram_sup_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}

	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src/generate_bigram.py \
					--input $logdir/out.JOB \
					--output $logdir/gen_JOB \
					--data $exp \
					--process $proc
	fi
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
# Concatenate the files together.
	log "Concatenate the files together"
	for n in $(seq $nj); do
		cat $logdir/gen_$n/transcripts.txt
	done > $outdir/transcripts.txt

	cp $logdir/gen_*/*.wav $outdir/
	# check if all lines were processed
	nf=$(wc -l < $input_text)
	nu=$(wc -l < $outdir/transcripts.txt)
	if [ $nf -ne $nu ]; then
		log "Warning $0: It seems not all of the lines were successfully procesed" 
		log "$nu out of $nf were processed"
	fi
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then

	log "creating $mode directory with wav.scp, text, fake utt2spk"
	mkdir $mode
	python utils/make_wav_scp.py --audio-dir $outdir --out-dir $mode
	cp $outdir/transcripts.txt $mode/text
	cat $mode/wav.scp | awk '{print $1 " " $1}' > $mode/utt2spk
	cp $mode/utt2spk $mode/spk2utt

fi
