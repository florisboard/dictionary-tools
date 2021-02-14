import io
from typing import Dict, Optional
import unicodedata

__FLICT_CMD_BEGIN_HEADER =      0x1
__FLICT_CMD_BEGIN_SECTION =     0x2
__FLICT_CMD_END =               0x3

__FLICT_BEGIN_SECTION_128 =     0x00
__FLICT_BEGIN_SECTION_16384 =   0x80
__FLICT_BEGIN_HEADER =          0xC0
__FLICT_END =                   0xF0

class FlictNode:
    def __init__(self, freq: Optional[int] = None):
        self.children: Dict[str, FlictNode] = {}
        self.freq: Optional[int] = freq

    # def optimize(self) -> list:
    #     ret_list = []
    #     if self.freq != None and len(self.children) == 0:
    #         # Is opaque end point
    #         ret_list.insert(0, self)
    #     elif self.freq == None and len(self.children) == 1:
    #         self.children[self.children.keys[0]]

class FlictRootNode(FlictNode):
    def __init__(self):
        self.children: Dict[str, FlictNode] = {}
        self.header: Optional[str] = None
        self.freq: Optional[int] = None

def __encode_cmd_block(byte_arr: bytearray, cmd: int, v: int):
    if cmd == __FLICT_CMD_END:
        if v > 0:
            if v < 16:
                byte_arr.append(__FLICT_END | (v & 0x0F))
            else:
                raise ValueError("Given attribute v used as end-counter must be smaller than 16!")
        else:
            raise ValueError("Given attribute v used as end-counter must be greater than 0!")
    elif cmd == __FLICT_CMD_BEGIN_SECTION:
        if v > 0:
            if v < 128:
                byte_arr.append(__FLICT_BEGIN_SECTION_128 | (v & 0x7F))
            elif v < 16384:
                byte_arr.append(__FLICT_BEGIN_SECTION_16384 | ((v >> 8) & 0x3F))
                byte_arr.append(v & 0xFF)
            else:
                raise ValueError("Given attribute v used as size must be smaller than 16834!")
        else:
            raise ValueError("Given attribute v used as size must be greater than 0!")
    elif cmd == __FLICT_CMD_BEGIN_HEADER:
        if v > 0:
            if v < 8192:
                byte_arr.append(__FLICT_BEGIN_HEADER | ((v >> 8) & 0x1F))
                byte_arr.append(v & 0xFF)
            else:
                raise ValueError("Given attribute v used as size must be smaller than 8192!")
        else:
            raise ValueError("Given attribute v used as size must be greater than 0!")
    else:
        raise ValueError("Given cmd is invalid!")

def __encode_inner(byte_arr: bytearray, word: str, node: FlictNode):
    word_bytes = bytearray(word, "utf-8")
    __encode_cmd_block(byte_arr, __FLICT_CMD_BEGIN_SECTION, len(word_bytes))
    if node.freq != None:
        byte_arr.append(node.freq & 0xFF)
    else:
        byte_arr.append(0x00)
    byte_arr.extend(word_bytes)
    for key in node.children:
        __encode_inner(byte_arr, key, node.children[key])
    last_byte = byte_arr[-1]
    if last_byte & 0xF0 == 0xF0:
        if last_byte & 0x0F == 15:
            __encode_cmd_block(byte_arr, __FLICT_CMD_END, 1)
        else:
            del byte_arr[-1]
            __encode_cmd_block(byte_arr, __FLICT_CMD_END, (last_byte & 0x0F) + 1)
    else:
        __encode_cmd_block(byte_arr, __FLICT_CMD_END, 1)

def __encode(node: FlictRootNode):
    byte_arr = bytearray()
    if node.header != None:
        header_str = bytearray(node.header, "utf-8")
        __encode_cmd_block(byte_arr, __FLICT_CMD_BEGIN_HEADER, len(header_str))
        byte_arr.extend(header_str)
        __encode_cmd_block(byte_arr, __FLICT_CMD_END, 1)
    for key in node.children:
        __encode_inner(byte_arr, key, node.children[key])
    return byte_arr

def clb_to_flict(src_path: str, dst_path: str):
    try:
        flict_tree = FlictRootNode()
        with io.open(src_path, "r", encoding="utf-8") as f_src:
            is_first = True
            for line in f_src.readlines():
                if is_first:
                    # Treat as header
                    flict_tree.header = line.rstrip()
                    is_first = False
                else:
                    line_list = line.rstrip()[6:].split(",f=")
                    word = unicodedata.normalize("NFC", line_list[0])
                    freq = int(line_list[1])
                    flict_tree_node = flict_tree
                    pos = 0
                    for c in word:
                        if not c in flict_tree_node.children:
                            flict_tree_node.children[c] = FlictNode(None)
                        if pos + 1 >= len(word):
                            flict_tree_node.children[c].freq = freq
                        else:
                            flict_tree_node = flict_tree_node.children[c]
                        pos += 1

        with io.open(dst_path, "wb") as f_dst:
            f_dst.write(__encode(flict_tree))
        return True
    except ValueError as e:
        print(e)
        return False

#clb_to_flict("./.dicttool/combined-list-en.txt", "./.dicttool/en.flict")
