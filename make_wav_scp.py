import os 
dir = "/ocean/projects/cis210027p/dzeinali/espnet_cs/egs2/seame/asr1/speechCollage/exp/random_hammin_np/audios/" #directory of audios 
with open("/ocean/projects/cis210027p/dzeinali/espnet_cs/egs2/seame/asr1/data/train_seame_random_hamming/wav.scp","w") as f: 
    for file in os.listdir(dir): 
    
        if file.endswith(".wav"): 
    
            f.write(file.split(".")[0] + " " + dir + file+"\n") 


