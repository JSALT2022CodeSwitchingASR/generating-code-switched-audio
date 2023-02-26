#!/bin/bash 

utils=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils
cmd=/alt-arabic/speech/amir/kaldi/egs/wsj/s5/utils/parallel/slurm.pl
nj=100
logdir="/jsalt2/amir/generating-code-switched-audio2/slurm_log"
mkdir -p $logdir
mode=unigrams # unigrams, bigrams

inputlist="/jsalt2/amir/generating-code-switched-audio2/data/text_60K " #input transcript for generation
outdir="/jsalt2/amir/generating-code-switched-audio2/exp/${mode}" #desired output directory for audios 
data="/jsalt2/amir/generating-code-switched-audio2/exp/" #where json dictionaries of supervisions and recordings are stored
proc=1

# split file to number of jobs
split_scps=
for n in $(seq $nj); do
    split_scps="$split_scps $logdir/out.$n"
done
echo "Splitting $inputlist into $nj"

$utils/split_scp.pl $inputlist $split_scps

mkdir -p $outdir
# run array jobs 
echo "run array jobs"
$cmd JOB=1:$nj $logdir/out.JOB.log \
	./src2/generate_unigram.py \
			  --input $logdir/out.JOB \
			  --output $logdir/gen_JOB \
			  --data $data \
			  --process $proc

# Concatenate the files together.
for n in $(seq $nj); do
  cat $logdir/gen_$n/transcripts.txt
done > $outdir/transcripts.txt

cp $logdir/gen_*/*.wav $outdir/
# check if all lines were processed
nf=$(wc -l < $inputlist)
nu=$(wc -l < $logdir/transcripts.txt)
if [ $nf -ne $nu ]; then
  echo "$0: It seems not all of the lines were successfully procesed" 
fi