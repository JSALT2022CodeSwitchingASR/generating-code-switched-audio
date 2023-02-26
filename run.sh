#!/bin/bash 

# function to print logs
log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

utils=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils
cmd=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils/parallel/slurm.pl
nj=100		# number of jobs across the nodes
mode=unigram_imp 	# different modes to generate the code switching: unigram, unigram_imp, bigrams
logdir="/jsalt2/amir/generating-code-switched-audio2/slurm_log_${mode}"
mkdir -p $logdir
indir="/jsalt2/amir/generating-code-switched-audio2/data"
inputlist="${indir}/text_60K" #input transcript for generation
outdir="/jsalt2/amir/generating-code-switched-audio2/exp/${mode}" #desired output directory for audios 
exp="/jsalt2/amir/generating-code-switched-audio2/exp/data_${mode}" #where json dictionaries of supervisions and recordings are stored
mkdir -p $exp
proc=1

# split file to number of jobs
log "Splitting $inputlist into $nj jobs"

split_scps=
for n in $(seq $nj); do
    split_scps="$split_scps $logdir/out.$n"
done

$utils/split_scp.pl $inputlist $split_scps

mkdir -p $outdir
# run array jobs 
log "running array jobs"
if [ $mode == unigram ]; then 
	log "Preparing recordings dict: python src2/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
	python src2/setup_recording_dict.py ${indir}/wav.scp ${exp}

	log "Preparing supervisions: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
	python src2/setup_supervision_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}

	log "Generating audio with $mode mode"
	$cmd JOB=1:$nj $logdir/out.JOB.log \
		./src2/generate_unigram.py \
				  --input $logdir/out.JOB \
				  --output $logdir/gen_JOB \
				  --data $exp \
				  --process $proc
				  
elif [ $mode == "unigram_imp" ]; then
	log "Preparing recordings dict: python src2/setup_recording_dict.py ${indir}/wav.scp ${outdir}"
	python src2/setup_recording_dict.py ${indir}/wav.scp ${exp}

	log "Preparing supervisions with hamming window: python setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}"
	python src2/setup_supervision_improved_dict.py ${indir}/ctm.mono ${exp}/recording_dict.json ${exp}

	log "Generating audio with $mode mode"
	$cmd JOB=1:$nj $logdir/out.JOB.log \
		./src2/generate_unigram_improved.py \
				  --input $logdir/out.JOB \
				  --output $logdir/gen_JOB \
				  --data $exp \
				  --process $proc
fi

# Concatenate the files together.
for n in $(seq $nj); do
  cat $logdir/gen_$n/transcripts.txt
done > $outdir/transcripts.txt

cp $logdir/gen_*/*.wav $outdir/
# check if all lines were processed
nf=$(wc -l < $inputlist)
nu=$(wc -l < $logdir/transcripts.txt)
if [ $nf -ne $nu ]; then
  log "$0: It seems not all of the lines were successfully procesed" 
  log "$nu out of $nf were processed"
fi