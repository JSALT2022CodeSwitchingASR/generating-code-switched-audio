#!/usr/bin/env python3
# -*- encoding: utf8 -*-

import os
import argparse

alph = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
alph_lower = [x.lower() for x in alph]
num = ["0","1","2","3","4","5","6","7","8","9"]
eng_set = alph + alph_lower + num

def lid(c):
    if c[0] in eng_set:
        return "<en>"
    else:
        return "<zh>"

def add_lid(x):
    if len(x) == 1:
        id = x[0]
        txt = ""
    else:
        id = x[0]
        txt = x[1]
    new_txt = []
    prev = ""
    for i, c in enumerate(txt.split()):
        curr = lid(c)
        if c != "<noise>" and curr != prev:
            new_txt.append(curr)
            prev = curr
        new_txt.append(c)
    return id + " " + " ".join(new_txt) + "\n"
        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    args = parser.parse_args()


    lines = [x.strip().split(" ", 1) for x in open(args.src, "r").readlines()]
    new_lines = [add_lid(x) for x in lines]
    
    with open(args.src + "_lid", "w") as f:
        f.writelines(new_lines)
