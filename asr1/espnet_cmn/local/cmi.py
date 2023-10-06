
import os
import argparse

alph = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
alph_lower = [x.lower() for x in alph]
num = ["0","1","2","3","4","5","6","7","8","9"]
eng_set = alph + alph_lower + num
tagset = ["<en>", "<zh>", "<other>"]

def lid(c):
    if len(c) == 0:
        return ""
    if c[0] in eng_set:
        return "<en>"
    else:
        return "<zh>"

def add_lid(x):
    id_, txt = x[0], x[1:]
    new_txt = []
    new_txt.append(id_)
    prev = ""
    for i, c in enumerate(txt):
        curr = lid(c)
        if c != "<noise>":
            new_txt.append(curr)
            prev = curr
        #new_txt.append(c)
    return " ".join(new_txt) + "\n"


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
    for tag in utterance:
        if tag == '' or tag is None:
            print("No tag for word ")
        elif tag in tagset:
            tags[tagset.index(tag)] += 1
            P, currlang = switchpoint(tag, tagset, P, currlang)

    lang = sum(tags) - tags[-1]
    nummatrix = max(tags)
    if lang == 0:
        return 0, P, tags
    else:
        return 1/2 - (nummatrix - P)/(2*lang), P, tags



if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    args = parser.parse_args()

    cmi_sum = 0
    lines = [x.strip().split(" ") for x in open(args.src, "r").readlines()]
    breakpoint()
    new_lines = [add_lid(x) for x in lines]
    
    # with open(args.src + "_lid", "w") as f:
    #     f.writelines(new_lines)
    
    for line in new_lines:
        text = line.strip().split(" ")[1:]
        cmi, _, _ = cmi_one_utterance(text,tagset)
        cmi_sum += cmi*100
    cmi_avg = round(cmi_sum/len(lines),2)
    print(f"Avg CMI percentage: {cmi_avg}")
