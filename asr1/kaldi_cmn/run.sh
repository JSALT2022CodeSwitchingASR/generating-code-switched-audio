#!/bin/bash

# Copyright (C) 2022, Johns Hopkins University
#               Amir Hussein
# Apache 2.0

stage=6
export LC_ALL=en_US.UTF-8

data='data'

. ./path.sh
. ./cmd.sh

. utils/parse_options.sh


set -e -o pipefail -u


nj=100  # split training into how many jobs?
nDecodeJobs=100

##########################################################
#
#  Recipe
#
##########################################################


#1) Data preparation

if [ $stage -le 1 ]; then
  # DATA PREPARATION
  echo "Preparing data"
  utils/combine_data.sh data/train data/train_*
  
fi

lm=$data/local/lm
if [ $stage -le 2 ]; then
  #DICTIONARY PREPARATION
  echo "Preparing dictionary"
  # if [ ! -d $lm ]; then
  #   mkdir -p $lm
  # fi
  # cat $data/train/text | cut -d " " -f2- | perl -pe 's/\.\n/\n/' | perl -pe 's/\./\n/' \
  # | tr ' ' '\n'| tr '[:upper:]' '[:lower:]' | sort -u | sed -r '/^\s*$/d' > $lm/words.txt
  
  #L Compilation
  echo "Preparing lang dir"
  #./local/prepare_dict.sh $lm $data/local/dict
  ./local/prep_dict_en_zh.sh

  ./utils/prepare_lang.sh --position-dependent-phones false data/local/dict "<UNK>" data/local/lang data/lang
fi

# Using the training data transcript for building the language model

# cat $data/train/text | cut -d " " -f2- | perl -pe 's/\.\n/\n/' | \
# perl -pe 's/\./\n/' > $lm/train_text


if [ $stage -le 3 ]; then
  #LM TRAINING: Using the training set transcript text for language modelling
  echo "Training n-gram language model"
  # local/train_lms_extra.sh $lm/train_text
  bash local/train_lms.sh
fi

if [ $stage -le 4 ]; then
  #Calculating mfcc features
  mfccdir=mfcc
  echo "Computing features"
  for x in train dev; do
    steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" $data/$x \
      exp/make_mfcc/$x/log $mfccdir
    steps/compute_cmvn_stats.sh $data/$x \
      exp/make_mfcc/$x/log $mfccdir
    utils/fix_data_dir.sh $data/$x
  done
fi

if [ $stage -le 5 ]; then
  #G compilation
  echo "G compilation"
  local/format_data.sh --lang-test $data/lang \
    --arpa-lm $data/local/lm/3gram-mincount/lm_unpruned.gz
  
  # utils/build_const_arpa_lm.sh data/local/ngram/4gram-mincount/lm_unpruned.gz \
  #   $data/lang $data/lang_test_4g
fi



if [ $stage -le 6 ]; then
  #Taking 5k segments for faster training  
  utils/subset_data_dir.sh $data/train 5000 $data/train_5k
  utils/subset_data_dir.sh $data/train 10000 $data/train_10k
fi

if [ $stage -le 7 ]; then
  #Monophone training
  steps/train_mono.sh --boost-silence 1.25 --totgauss 1000 --nj $nj --cmd "$train_cmd" \
    $data/train_5k $data/lang exp/mono 
  # Decode with mono
  utils/mkgraph.sh --mono $data/lang exp/mono exp/mono/graph
  for dev in dev; do
    steps/decode.sh --config conf/decode.config \
    --cmd "$decode_cmd" --nj $nDecodeJobs exp/mono/graph data/$dev exp/mono/decode_$dev
  done

fi

if [ $stage -le 8 ]; then
  #Monophone alignment
  steps/align_si.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" \
    $data/train_5k $data/lang exp/mono exp/mono_ali

  #tri1 [First triphone pass]
  steps/train_deltas.sh --cmd "$train_cmd" \
    2000 10000 $data/train_5k $data/lang exp/mono_ali exp/tri1 

  #tri1 decoding
  utils/mkgraph.sh $data/lang exp/tri1 exp/tri1/graph

  for dev in dev; do
    steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
      exp/tri1/graph $data/$dev exp/tri1/decode_$dev &
  done
fi

if [ $stage -le 9 ]; then
  #tri1 alignment
  nj=100
  steps/align_si.sh --nj $nj --cmd "$train_cmd" \
    $data/train_10k $data/lang exp/tri1 exp/tri1_ali 

  #tri2 [a larger model than tri1]
  steps/train_deltas.sh --cmd "$train_cmd" \
    2500 20000 $data/train_10k $data/lang exp/tri1_ali exp/tri2

  #tri2 decoding
  utils/mkgraph.sh data/lang exp/tri2 exp/tri2/graph

  for dev in dev; do
   steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
   exp/tri2/graph data/$dev exp/tri2/decode_$dev &
  done
fi

if [ $stage -le 10 ]; then
  #tri2 alignment
  steps/align_si.sh --nj $nj --cmd "$train_cmd" \
    $data/train $data/lang exp/tri2 exp/tri2_ali

  # tri3 training [LDA+MLLT]
  steps/train_lda_mllt.sh --cmd "$train_cmd" \
    3500 20000 $data/train $data/lang exp/tri2_ali exp/tri3

  #tri3 decoding
  utils/mkgraph.sh $data/lang exp/tri3 exp/tri3/graph

  for dev in dev test; do
   steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
   exp/tri3/graph $data/$dev exp/tri3/decode_$dev & 
  done
fi

if [ $stage -le 11 ]; then
  #tri3 alignment
  #steps/align_si.sh --nj $nj --cmd "$train_cmd" --use-graphs true data/train_mer${mer}_subset500 data/lang exp/mer$mer/tri3 exp/mer$mer/tri3_ali
  steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" $data/train \
  $data/lang exp/tri3 exp/tri3_ali
  #now we start building model with speaker adaptation SAT [fmllr]
  steps/train_sat.sh  --cmd "$train_cmd" \
    4200 40000 $data/train $data/lang exp/tri3_ali exp/tri4

  #sat decoding
  utils/mkgraph.sh $data/lang exp/tri4 exp/tri4/graph

  for dev in dev; do
    steps/decode_fmllr.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
      exp/tri4/graph $data/$dev exp/tri4/decode_$dev &
  done
fi

exit 0;
