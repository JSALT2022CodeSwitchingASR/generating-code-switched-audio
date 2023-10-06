#!/usr/bin/env bash

set -e -o pipefail
stage=0
nj=30
mer=80 
train_set=train_mer$mer
                 # should have alignments for the specified training data.
nnet3_affix=       # affix for exp dirs, e.g. it was _cleaned in tedlium.

# Options which are not passed through to run_ivector_common.sh
affix=_1a   #affix for TDNN+LSTM directory e.g. "1a" or "1b", in case we change the configuration.
common_egs_dir=
reporting_email=
test_sets=$1
data_dir=$2

# training chunk-options
chunk_width=150,110,100

# End configuration section.
echo "$0 $@"  # Print the command line for logging


. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh


if ! cuda-compiled; then
  cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
fi

lat_dir=exp/mer$mer/chain${nnet3_affix}/${gmm}_${train_set}_sp_lats
dir=exp/mer$mer/chain${nnet3_affix}/tdnn${affix}_sp

tree_dir=exp/mer$mer/chain${nnet3_affix}/tree_a_sp

mfccdir=mfcc
for test_set in ${test_sets}; do 
    #nj=200
	nj=$(wc -l < data/$data_dir/${test_set}/spk2utt)
	steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" --write-utt2dur false data/$data_dir/${test_set}
	steps/compute_cmvn_stats.sh data/$data_dir/$test_set
	utils/fix_data_dir.sh data/$data_dir/$test_set
	
	steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj $nj \
     data/$data_dir/${test_set} exp/mer$mer/nnet3${nnet3_affix}/extractor \
     exp/mer$mer/nnet3${nnet3_affix}/$data_dir/ivectors_${test_set}
	 
	#steps/online/nnet2/extract_ivectors.sh --nj $nj --cmd "$train_cmd" \
	#  data/$test_set data/lang exp/mer80/nnet3/extractor exp/mer80/nnet3/ivectors_$test_set
done


#nj=200
nj=$(wc -l < data/$data_dir/${test_set}/spk2utt)
if [ $stage -le 18 ]; then
	echo "decoding "
  frames_per_chunk=$(echo $chunk_width | cut -d, -f1)
  rm $dir/.error 2>/dev/null || true
    for test_set in ${test_sets}; do 
    (
    ./decode.sh \
      --acwt 1.0 --post-decode-acwt 10.0 \
      --extra-left-context 0 --extra-right-context 0 \
      --extra-left-context-initial 0 \
      --extra-right-context-final 0 \
      --frames-per-chunk $frames_per_chunk \
      --nj $nj --cmd "$decode_cmd"  --num-threads 4 \
      --online-ivector-dir exp/mer$mer/nnet3${nnet3_affix}/$data_dir/ivectors_${test_set} \
      $tree_dir/graph data/$data_dir/${test_set} ${dir}/${data_dir}/${test_set} exp/mer80/chain_all/tdnn_1a_sp/final.mdl || exit 1 
	     
		 
    steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" data/lang_test{,_fg} \
      data/$data_dir/${test_set} ${dir}/${data_dir}/${test_set} ${dir}/${data_dir}/${test_set}_rescore || exit 1 
	     ) || touch $dir/.error &
  done
  wait
  if [ -f $dir/.error ]; then
    echo "$0: something went wrong in decoding"
    exit 1
  fi
fi

