import clb
import makeall
import os
import shutil
import sys

def __make_dict(src_path, dst_path):
    return os.system("java -jar dicttool_aosp.jar makedict -s {} -d {}".format(src_path, dst_path))

def __print_usage():
    print(
    """
    {} <command> [<arguments>]\n
    Available commands:
        clean       Cleans up the .dicttool folder in this directory
        help        Shows this help dialog
        make        Makes a single dictionary with these required arguments:
                     <lang_code> <src_type> <src_path>
        makeall     Makes all dictionares defined in the static list in makeall.py
    """.format(sys.argv[0])
    )

def make(src_def):
    lang_code = src_def[0]
    src_type = src_def[1]
    src_path = src_def[2]
    print(
    """
    # Make dictionary for
        lang_code = {}
        src_type = {}
        src_path = {}
    """.format(lang_code, src_type, src_path)
    )
    os.makedirs(".dicttool", exist_ok=True)
    clb_path = ".dicttool/combined-list-{}.txt".format(lang_code)
    dst_path = ".dicttool/main_{}.dict".format(lang_code)
    if src_type == "cBpack":
        clb.cBpack(lang_code, src_path, clb_path)
    else:
        print("      Error: Unsupported src_type provided. Skipping this entry...\n")
        return False
    if __make_dict(clb_path, dst_path) == 0:
        print("      Success: Finished building dictionary!\n")
        return True
    else:
        print("      Error: AOSP dictionary tool encountered an error. Skipping item...\n")
        return False

def main():
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "clean":
            shutil.rmtree(".dicttool")
        elif cmd == "help":
            __print_usage()
        elif cmd == "make":
            if len(sys.argv) == 5:
                make(sys.argv[2:5])
            else:
                print("    Failed to initiate 'make': required 3 argument condition failed.")
        elif cmd == "makeall":
            for src_def in makeall.LIST:
                make(src_def)
            print("___\nFinished.\n")
    else:
        __print_usage()

if __name__ == "__main__":
    main()
