import sys 
from pathlib import Path
import pdb

def seg2rec_ctm(data_dir):

    ctm_lines = open(data_dir / "ctm.mono",'r').readlines()
    seg_lines = open(data_dir / "segments",'r').readlines()
    seg_dict = {}
    for l in seg_lines:
        l = l.strip().split()
        seg_dict[l[0]] = (l[1], l[2], l[3]) 
    new_ctm_lines = []
    for l in ctm_lines:
        l = l.strip().split()
        start = float(seg_dict[l[0]][1]) + float(l[2])
        ctm_line = " ".join([seg_dict[l[0]][0], l[1], 
                                str(round(start,3)), l[3], l[4]])
        new_ctm_lines.append(ctm_line+"\n")
        
    with open('ctm', 'w') as f:  
        for line in new_ctm_lines:      
            f.write(line)

if __name__ == "__main__": 
	seg2rec_ctm(Path(sys.argv[1]))