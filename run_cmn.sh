#!/bin/bash 

# Copyright 2023 Jons Hopkins University (Amir Hussein)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)


# function to print logs
log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

process_ctm=false
lang=cmn
stage=-1
stop_stage=3
utils=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils
cmd=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils/parallel/slurm.pl
nj=100		# number of jobs across the nodes
mode=unigram 	# different modes to generate the code switching: unigram, unigram_imp, bigrams
logdir="/jsalt2/amir/generating-code-switched-audio2/slurm_log_${lang}_${mode}"

indir="/jsalt2/amir/generating-code-switched-audio2/data_cmn"
inputlist="${indir}/text" 	# input transcript for generation
outdir="/jsalt2/amir/generating-code-switched-audio2/exp_cmn/${mode}" 	# desired output directory for audios 

exp="/jsalt2/amir/generating-code-switched-audio2/exp_cmn/data_${mode}" 	# where json dictionaries of supervisions and recordings are stored


if [ ! -d "$exp" ]; then
  echo "$exp does not exist, creating  $exp"
  mkdir -p $exp
fi

proc=1
clean_dir=false

if [ $clean_dir == true ]; then
	log "removing $outdir and  $logdir"
	rm -rf $outdir
	rm -rf $logdir
fi

if [ ! -d "$logdir" ]; then
	echo "$logdir does not exist, creating new $logdir"
	mkdir -p $logdir
fi

if [ ${stage} -le -1 ] && [ ${stop_stage} -ge -1 ]; then
	if [ $process_ctm == true ]; then
		python src2/seg2rec_ctm.py $indir
	fi


	# split file to number of jobs
	log "Splitting $inputlist into $nj jobs"

	split_scps=
	for n in $(seq $nj); do
		split_scps="$split_scps $logdir/out.$n"
	done

	$utils/split_scp.pl $inputlist $split_scps

	mkdir -p $outdir
fi

# run array jobs 

if [ $mode == "unigram" ]; then 
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src2/setup_recording_dict.py ${indir}/wav.scp ${outdir}"

		python src2/setup_recording_dict.py ${indir}/wav.scp ${exp}

		log "Preparing supervisions: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"

		python src2/setup_supervision_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Stage 1: Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src2/generate_unigram.py \
					--input $logdir/out.JOB \
					--output $logdir/gen_JOB \
					--data $exp \
					--process $proc
	fi

elif [ $mode == "unigram_imp" ]; then
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src2/setup_recording_dict.py ${indir}/wav.scp ${outdir}"

		python src2/setup_recording_dict.py ${indir}/wav.scp ${exp}

		log "Preparing supervisions with hamming window: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}"

		python src2/setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src2/generate_unigram_improved.py \
					--input $logdir/out.JOB \
					--output $logdir/gen_JOB \
					--data $exp \
					--process $proc
	fi
elif [ $mode == "bigram" ]; then
	log "$mode running array jobs"
	if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
		log "Preparing recordings dict: python src2/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
		python src2/setup_recording_dict.py ${indir}/wav.scp ${exp}

		log "Preparing bigram supervisions: python src2/setup_supervision_bigram_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}"
		python src2/setup_supervision_bigram_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}

		log "Preparing unigram_imp supervisions: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}"
		python src2/setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.pkl ${exp}
	fi

	if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
		log "Generating audio with $mode mode"
		$cmd JOB=1:$nj $logdir/out.JOB.log \
			./src2/generate_bigram.py \
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

	for n in $(seq $nj); do
		log "copying wav files from gen_$n/"
		cp $logdir/gen_$n/*.wav $outdir/
	done
	# check if all lines were processed
	nf=$(wc -l < $inputlist)
	nu=$(wc -l < $outdir/transcripts.txt)
	if [ $nf -ne $nu ]; then
		log "$0: It seems not all of the text lines were successfully generated" 
		log "$nu out of $nf were generated"
	fi
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then

	log "creating ${mode}_${lang} directory with wav.scp, text, fake utt2spk"
	mkdir ${mode}_${lang}

	if [ ! -d "${mode}_${lang}" ]; then
		mkdir -p ${mode}_${lang}
	fi

	python make_wav_scp.py --audio-dir $outdir --out-dir ${mode}_${lang}
	cp $outdir/transcripts.txt ${mode}_${lang}/text
	cat ${mode}_${lang}/wav.scp | awk '{print $1 " " $1}' > ${mode}_${lang}/utt2spk
	cp ${mode}_${lang}/utt2spk ${mode}_${lang}/spk2utt

fi