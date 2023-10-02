#!/usr/bin/env python3
# -*- encoding: utf8 -*-

import os
import argparse

cnt = 0

def is_aishell(tag):
    if "BAC" in tag:
        global cnt
        cnt += 1
        return True
    return False

def add_lid(id, txt):
    if is_aishell(id):
        txt = "<zh> " + txt
    else:
        txt = "<en> " + txt
    return id + " " + txt + "\n"

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str)
    args = parser.parse_args()


    lines = [x.strip().split(" ", 1) for x in open(args.src, "r").readlines()]
    new_lines = [add_lid(id, txt) for id, txt in lines]
    print(cnt)
    
    with open(args.src, "w") as f:
        f.writelines(new_lines)
