# Speech Collage

This repository contains the code used for the paper titled [SPEECH COLLAGE: CODE-SWITCHED AUDIO GENERATION BY COLLAGING
MONOLINGUAL CORPORA"](https://arxiv.org/pdf/2309.15674.pdf).

## Requirements

### Python environment

- python version ` 3.8.12 `
- To create anaconda environment run `conda env create -f environment.yml`


### Install neccesary toolkits
1- Install espnet and kaldi https://espnet.github.io/espnet/installation.html 
2- Install SOX format libraries
`sudo apt-get install libsox-fmt-all`


## Steps to generate audio from monolingual data
1- Train standard HMM-GMM ASR system following standard Kaldi recipies for you monolingual data https://github.com/kaldi-asr/kaldi. You can also follow the provided monolingual Chinese-English (Aishel+Tedlium3) recipe `asr1/kaldi/`

2- Generate the alignments (ctm) file using kaldi script `steps/get_train_ctm.sh` and save it in your `data_dir`. In addition copy the `text` (in our case code-switching) used for generation. Note here that you can use any text as long as you have the monolingual audios for that text. 

To generate the ctm using kaldi: `steps/get_train_ctm.sh --use-segments false data/train data/lang exp/tri3_ali data_dir/ctm.mono`

If the first column of `ctm` file is segments you will have to run `src/seg2rec_ctm.py data_dir` to convert the segments to the names of audio recordings from wav.scp.

3- Following the kaldi style copy `wav.scp` file containing monolingual utterances to `data_dir`. Generate a recording dictionary as following:

`python src/setup_recording_dict.py ${indir}/wav.scp outdir`

4- With ctm file for the monolingual utterances and recording dictionary, create a supervision 
dictionary. 
For randomly generated utterances with unigram units and no signal enhancement:

`python src/setup_supervision_dict.py data_dir/ctm.mono outdir/recording_dict.pkl outdir`

For randomly generated utterances with unigram units and signal enhancement:

`python src/setup_supervision_improved_dict.py data_dir/ctm.mono outdir/recording_dict.pkl outdir`

For randomly generated utterances with bigrams units and signal enhancement:

`python src/setup_bigram_sup_dict.py data_dir/ctm.mono outdir/recording_dict.pkl outdir`


5- Run the audio generation. Below is an example for generating bigrams
```
./src/generate_bigram.py \
					--input text \
					--output outdir/bigrams \
					--data outdir \
					--jobs $nj
```

6- Once the audios are generated, run `make_wav_scp.py` to create wav.scp file.

`python utils/make_wav_scp.py --audio-dir outdir/bigrams --out-dir data_dir_mode`

7- Create the rest of the files: text, utt2spk, spk2utt:

```
cp outdir/bigrams/transcripts.txt data_dir_mode/text
cat data_dir_mode/wav.scp | awk '{print $1 " " $1}' > data_dir_mode/utt2spk
cp data_dir_mode/utt2spk data_dir_mode/spk2utt
```

8- Now use `data_dir_mode` data folder for Espnet training

Note: You can follow `run.sh` for all the steps above.

## Cite Paper:
```
@article{hussein2023speech,
  title={Speech collage: code-switched audio generation by collaging monolingual corpora},
  author={Hussein, Amir and Zeinali, Dorsa and Klejch, Ond{\v{r}}ej and Wiesner, Matthew and Yan, Brian and Chowdhury, Shammur and Ali, Ahmed and Watanabe, Shinji and Khudanpur, Sanjeev},
  journal={arXiv preprint arXiv:2309.15674},
  year={2023}
}
```




