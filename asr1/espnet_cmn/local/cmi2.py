
import os
import argparse
from jiwer import wer

alph = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
alph_lower = [x.lower() for x in alph]
num = ["0","1","2","3","4","5","6","7","8","9"]
eng_set = alph + alph_lower
tagset = ["<en>", "<zh>", "<other>"]

def lid(c):
    if len(c) == 0:
        return ""
    if c[0] in eng_set:
        return "<en>"
    else:
        return "<zh>"

def add_lid(txt):
    #id_, txt = x[0], x[]
    new_txt = []
    #new_txt.append(id_)
    prev = ""
    for i, c in enumerate(txt):
        if c != " ":
            curr = lid(c)
            if c != "<noise>":
                new_txt.append((c,curr))
                prev = curr
        #new_txt.append(c)
    return new_txt


# Define the switchpoint function (simplified version)
def switchpoint(tag, tagset, P, currlang):
    langs = tagset
    if currlang == 0 and (tag in langs):
        return P, tag
    elif tag != currlang and (tag in langs):
        return P+1, tag
    else:
        return P, currlang

def cmi_one_utterance(utterance, tagset):
    P = 0
    currlang = 0
    tags = [0 for x in range(len(tagset))]
    
    # For simplicity, we'll assume each word is a tuple (word, tag)
    for (word, tag) in utterance:
        if tag == '' or tag is None or word == ' ':
            print(f"No tag for word {word}")
        elif tag in tagset:
            tags[tagset.index(tag)] += 1
            P, currlang = switchpoint(tag, tagset, P, currlang)

    lang = sum(tags) - tags[-1]
    nummatrix = max(tags)
    if lang == 0:
        return 0, P, tags
    else:
        return 1/2 - (nummatrix - P)/(2*lang), P, tags




def read_lines(args):
    src_dict, ref_dict = {},{}
    # with open(src, 'r') as a, open(ref, 'r') as b:
    #     src_lines = a.readlines()
    #     ref_lines = b.readlines()
    src_lines = [x.strip().split(" ") for x in open(args.src, "r").readlines()]
    ref_lines = [x.strip().split(" ") for x in open(args.ref, "r").readlines()]
    # for line in sorted(src_lines, key=cmp_to_key(locale.strcoll)):
    #     new_src.append(line)
    # for line in sorted(ref_lines, key=cmp_to_key(locale.strcoll)):
    for a in src_lines:
        src_dict[a[0].lower()] = " ".join(a[1:]).strip()

        
    for b in ref_lines:

        ref_dict[b[0].lower()] = " ".join(b[1:]).strip() 

    return src_dict, ref_dict

def get_correct_lines(src_dict, ref_dict, per=0.3):
    new_src, new_ref = [],[]
    for id_ in src_dict:
        if id_ in ref_dict:
            error = wer(ref_dict[id_], src_dict[id_])
            if error <= per:
                new_src.append(src_dict[id_])
                new_ref.append(ref_dict[id_])
    return new_src, new_ref

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    parser.add_argument("--ref", type=str)
    args = parser.parse_args()
    src_dict, ref_dict = read_lines(args)

    cmi_sum = 0
    # lines = [x.strip().split(" ") for x in open(args.src, "r").readlines()]
    
    src_lines, _ = get_correct_lines(src_dict, ref_dict, per=0.3)
    
    new_lines = [add_lid(x.split()) for x in src_lines]
    
    # with open(args.src + "_lid", "w") as f:
    #     f.writelines(new_lines)
    for line in new_lines:
        #text = line.strip().split(" ")[1:]
        cmi, _, _ = cmi_one_utterance(line,tagset)
        cmi_sum += cmi*100
    cmi_avg = round(cmi_sum/len(src_lines),2)
    print(f"Avg CMI percentage: {cmi_avg}")
