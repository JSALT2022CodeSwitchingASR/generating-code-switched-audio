#!/bin/bash

# Copyright 2022 Johns Hopkins (Amir Hussein)

. ./path.sh || exit 1;

indir=$1
outdir=$2
sample_h=$3 # number of hours
i=0
dur=0

if [ ! -d $outdir ] ; then
	  mkdir -p $outdir
fi

if [ -f $indir/segments ] ; then
  while IFS= read -r line; do
  	((i=i+1))
  	dur_line=$(echo $line | awk '{x=$4-$3; print x}')
    dur=$(bc -l <<<"${dur}+${dur_line}/3600")
    #echo "line: $i duration: $dur"
  	if [ $(echo "$dur > $sample_h" | bc) -ne 0 ]; then
      echo "line: $i duration: $dur"
      head -n $i $indir/segments > $outdir/segments
      cp $indir/text $outdir/text
      cp $indir/wav.scp $outdir/wav.scp
      cp $indir/utt2spk  $outdir/utt2spk
  	  cp $indir/spk2utt $outdir/spk2utt
      utils/fix_data_dir.sh $outdir
      break
    fi
  	
  done < $indir/segments

else

  cat $indir/wav.scp | while read line; do  
    wav=$(echo $line | cut -d " " -f2-) 
    dur_line=$(soxi -D  $wav)
    dur=$(bc -l <<<"${dur}+${dur_line}/3600"); 
    ((i=i+1))
    if [ $(echo "$dur > $sample_h" | bc) -ne 0 ]; then
      echo "line: $i duration: $dur"
      head -n $i $indir/wav.scp > $outdir/wav.scp
      head -n $i $indir/text > $outdir/text
      cp $indir/utt2spk $outdir/utt2spk
  	  cp $indir/spk2utt $outdir/spk2utt
      utils/fix_data_dir.sh $outdir
      break
    fi
    done
fi