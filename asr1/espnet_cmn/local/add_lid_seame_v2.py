#!/usr/bin/env python3
# -*- encoding: utf8 -*-

# No ID version

import os
import argparse

alph = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
alph_lower = [x.lower() for x in alph]
num = ["0","1","2","3","4","5","6","7","8","9"]
eng_set = alph + alph_lower + num

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
        if c != "<noise>" and curr != prev:
            new_txt.append(curr)
            prev = curr
        new_txt.append(c)
    return " ".join(new_txt) + "\n"
        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    args = parser.parse_args()


    lines = [x.strip().split(" ") for x in open(args.src, "r").readlines()]
    new_lines = [add_lid(x) for x in lines]
    
    with open(args.src + "_lid", "w") as f:
        f.writelines(new_lines)
