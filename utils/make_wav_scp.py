import os 
import argparse
from pathlib import Path

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--audio-dir",
        type=str,
        default="data/",
        help="Directory of the generated audio",
    )

    parser.add_argument(
        "--out-dir",
        type=str,
        default="data/",
        help="Directory for wav.scp",
    )
    return parser


parser = get_parser()
args = parser.parse_args()
audio_dir = Path(args.audio_dir)
out_dir = Path(args.out_dir)
with open(out_dir / "wav.scp","w") as f: 
    for file in os.listdir(audio_dir): 
    
        if file.endswith(".wav"): 
    
            f.write(str(file).split(".")[0] + " " + str(audio_dir / file) +"\n") 


