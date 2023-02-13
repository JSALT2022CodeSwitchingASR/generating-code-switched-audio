import os

f=open('/ocean/projects/cis210027p/dzeinali/espnet_cs/egs2/seame/asr1/data/train_seame_random_hamming/text', 'r') 
utt2spk=open('/ocean/projects/cis210027p/dzeinali/espnet_cs/egs2/seame/asr1/data/train_seame_random_hamming/utt2spk', 'w') 
spk2utt=open('/ocean/projects/cis210027p/dzeinali/espnet_cs/egs2/seame/asr1/data/train_seame_random_hamming/spk2utt', 'w')
for line in f.readlines(): 
    l=line.split()[0] 
    eyedee=l.split("_")[0] 
    s=l + ' ' + eyedee+"\n"
    utt2spk.write(s) 
    s2=eyedee + ' ' + l + "\n" 
    spk2utt.write(s2)

