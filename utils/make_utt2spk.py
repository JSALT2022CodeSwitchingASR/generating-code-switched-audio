import os
import argparse
from pathlib import Path

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--text-dir",
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
text_dir = Path(args.text_dir)
out_dir = Path(args.out_dir)

f=open(text_dir / 'text', 'r') 
utt2spk=open(out_dir / 'utt2spk', 'w') 
spk2utt=open(out_dir / 'spk2utt', 'w')
for line in f.readlines(): 
    l = line.split()[0] 
    eyedee = l.split("_")[0] 
    s = l + ' ' + eyedee+"\n"
    utt2spk.write(s) 
    s2 = eyedee + ' ' + l + "\n" 
    spk2utt.write(s2)

