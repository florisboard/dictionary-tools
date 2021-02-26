#!/usr/bin/env python3
# encoding: utf-8

import clb
import flict
import makeall
import os
import shutil
import sys
import textwrap

def __make_dict(src_path: str, dst_path: str):
    return os.system(f"java -jar dicttool_aosp.jar makedict -s {src_path} -d {dst_path}")

def __print_usage():
    print(textwrap.dedent(
        f"""\
        {sys.argv[0]} <command> [<arguments>]\n
        Available commands:
            clean       Cleans up the .dicttool folder in this directory
            help        Shows this help dialog
            make        Makes a single dictionary with these required arguments:
                        <lang_code> <src_type> <src_path> <dst_type>
            makeall     Makes all dictionares defined in the static list in makeall.py
        """
    ))

def make(src_def):
    lang_code = src_def[0]
    src_type = src_def[1]
    src_path = src_def[2]
    dst_type = src_def[3]
    print(textwrap.dedent(
        f"""\
        # Make dictionary for
            lang_code = {lang_code}
            src_type = {src_type}
            src_path = {src_path}
            dst_type = {dst_type}
        """
    ))
    os.makedirs(".dicttool", exist_ok=True)
    clb_path = f".dicttool/combined-list-{lang_code}.txt"
    if src_type == "cBpack":
        clb.cBpack(lang_code, src_path, ".srcin/swearWords.txt", clb_path)
    else:
        print("    Error: Unsupported src_type provided. Skipping this entry...\n")
        return False
    if dst_type == "dict":
        dst_path = f".dicttool/main_{lang_code}.dict"
        if __make_dict(clb_path, dst_path) == 0:
            print("    Success: Finished building dictionary!\n")
            return True
        else:
            print("    Error: AOSP dictionary tool encountered an error. Skipping item...\n")
            return False
    elif dst_type == "flict":
        dst_path = f".dicttool/{lang_code}.flict"
        if flict.clb_to_flict(clb_path, dst_path):
            print("    Success: Finished building dictionary!\n")
            return True
        else:
            print("    Error: Flictionary builder encountered an error. Skipping item...\n")
            return False
    else:
        print("    Error: Unsupported dst_type provided. Skipping this entry...\n")
        return False

def main():
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "clean":
            shutil.rmtree(".dicttool")
        elif cmd == "help":
            __print_usage()
        elif cmd == "make":
            if len(sys.argv) == 6:
                make(sys.argv[2:6])
            else:
                print("Failed to initiate 'make': required 4 argument condition failed.")
        elif cmd == "makeall":
            for src_def in makeall.LIST:
                make(src_def)
            print("___\nFinished.\n")
    else:
        __print_usage()

if __name__ == "__main__":
    main()
