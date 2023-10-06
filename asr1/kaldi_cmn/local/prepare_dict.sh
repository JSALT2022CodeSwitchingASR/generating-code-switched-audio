#!/usr/bin/env bash


# Copyright (C) 2022, Johns Hopkins, 
#                   Amir Hussein


# run this from ../
export LC_ALL=en_US.UTF-8

local_lm=$1
dir=$2
mkdir -p $dir

#Dictionary preparation:
lexicon_raw_nosil=$dir/lexicon_nosil
cat $local_lm/words.txt | sed 's:\(.\):\1 :g' > $local_lm/uniq_grapheme
paste -d ' '  $local_lm/words.txt $local_lm/uniq_grapheme > $lexicon_raw_nosil

# silence phones, one per line.

silence_phones=$dir/silence_phones.txt
optional_silence=$dir/optional_silence.txt
nonsil_phones=$dir/nonsilence_phones.txt

echo "Preparing phone lists and clustering questions"
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence
# nonsilence phones; on each line is a list of phones that correspond
# really to the same base phone.
cat $lexicon_raw_nosil | cut -d ' ' -f2- | tr -s ' ' '\n' | sort -u > $nonsil_phones || exit 1;
# A few extra questions that will be added to those obtained by automatically clustering
# the "real" phones.  These ask about stress; there's also one for silence.
echo "$(wc -l <$silence_phones) silence phones saved to: $silence_phones"
echo "$(wc -l <$optional_silence) optional silence saved to: $optional_silence"
echo "$(wc -l <$nonsil_phones) non-silence phones saved to: $nonsil_phones"



(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
  cat - $lexicon_raw_nosil | uniq >$dir/lexicon.txt
  echo "Lexicon text file saved as: $dir/lexicon.txt"


exit 0

