#!/usr/bin/env bash
# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

stage=12
stop_stage=13

train_set="train_mono_cmn"
valid_set="valid"
test_sets="devman devsge"
asr_config=conf/tuning/train_asr_conformer.yaml
lm_config=conf/tuning/train_lm_lstm2.yaml
#inference_config=conf/decode_asr.yaml
inference_config=conf/decode_asr_lm.yaml

if [ ! -f "data/${train_set}/token.man.2" ]; then
    # must preprocess data first to get Mandarin character tokens
    if [ ${stage} -eq 1 ]; then
        ./asr.sh --stage 1 --stop_stage 1 --train_set "${train_set}" --valid_set "${valid_set}" --test_sets "${test_sets}"
        stage=2
    else
        echo "Error: data/${train_set}/token.man.2 does not exist! Run from stage=1 again."
        exit 1
    fi
fi

#man_chars=2622
bpe_nlsyms=""
source data/${train_set}/token.man.2  # for bpe_nlsyms & man_chars
nbpe=$((3000 + man_chars))  # 5626
# English BPE: 2000 / Mandarin: 2622 / other symbols: 4

./asr.sh \
    --nj 100 \
    --use_lm true \
    --inference_nj 100 \
    --ngpu 2 \
    --stage ${stage} \
    --stop_stage ${stop_stage} \
    --nbpe ${nbpe} \
    --bpe_nlsyms "${bpe_nlsyms}" \
    --speed_perturb_factors "0.9 1.0 1.1" \
    --max_wav_duration 30 \
    --asr_config "${asr_config}" \
    --lm_config "${lm_config}" \
    --inference_config "${inference_config}" \
    --train_set "${train_set}" \
    --valid_set "${valid_set}" \
    --test_sets "${valid_set} ${test_sets}" \
    --lm_train_text "data/${train_set}/text" \
    --bpe_train_text "data/${train_set}/text" \
    --score_opts "-e utf-8 -c NOASCII" \
    "$@"
