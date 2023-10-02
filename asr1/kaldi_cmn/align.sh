#!/usr/bin/env bash

. ./path.sh
. ./cmd.sh

. utils/parse_options.sh


set -e -o pipefail -u

# feature extraction
stage=2
mfccdir=mfcc
data_set=train
nj=100
echo "Computing features"

if [ $stage -le 0 ]; then
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/$data_set \
    exp/mer/make_mfcc/$data_set/log $mfccdir
steps/compute_cmvn_stats.sh data/$data_set \
    exp/mer/make_mfcc/$data_set/log $mfccdir
utils/fix_data_dir.sh data/$data_set
fi

if [ $stage -le 1 ]; then
# # perform alignments
steps/align_fmllr.sh --nj 100 --cmd "$train_cmd" data/$data_set data/lang exp/tri4 exp/tri4_ali

fi

if [ $stage -le 2 ]; then
# produce ctm alignments

#steps/get_train_ctm.sh --use-segments false data/$data_set data/lang exp/tri4_ali exp/tri4_ali_ctm
steps/get_train_ctm.sh --use-segments false data/$data_set data/lang exp/tri3_ali exp/ctm

fi