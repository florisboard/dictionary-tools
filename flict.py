#!/usr/bin/env python3
# encoding: utf-8

import io
from typing import Dict, List, Optional, Sized
import unicodedata

class FlictSpec:
    VERSION_0 =                         0x0

    MASK_BEGIN_PTREE_NODE =             0x80
    CMDB_BEGIN_PTREE_NODE =             0x00
    ATTR_PTREE_NODE_ORDER =             0x70
    ATTR_PTREE_NODE_TYPE =              0x0C
    ATTR_PTREE_NODE_TYPE_CHAR =         0
    ATTR_PTREE_NODE_TYPE_WORD_FILLER =  1
    ATTR_PTREE_NODE_TYPE_WORD =         2
    ATTR_PTREE_NODE_TYPE_SHORTCUT =     3
    ATTR_PTREE_NODE_SIZE =              0x03

    MASK_END =                          0xC0
    CMDB_END =                          0x80
    ATTR_END_COUNT =                    0x3F
    ATTR_END_COUNT_MIN =                0x01
    ATTR_END_COUNT_MAX =                0x3F

    MASK_BEGIN_HEADER =                 0xE0
    CMDB_BEGIN_HEADER =                 0xC0
    ATTR_HEADER_VERSION =               0x1F

    MASK_DEFINE_SHORTCUT =              0xF0
    CMDB_DEFINE_SHORTCUT =              0xE0

    ATTR_DATE_MIN =                     0x00000000
    ATTR_DATE_MAX =                     0x7FFFFFFF
    ATTR_FREQ_MIN =                     0x00
    ATTR_FREQ_MAX =                     0xFF

    @staticmethod
    def isValidVersion(v: int) -> bool:
        return True if v == FlictSpec.VERSION_0 else False

    @staticmethod
    def writeCmd(
        byte_arr: bytearray,
        cmd: int,
        date: Optional[int] = None,
        end_count: Optional[int] = None,
        freq: Optional[int] = None,
        order: Optional[int] = None,
        size: Optional[int] = None,
        type: Optional[int] = None,
        version: Optional[int] = None
    ):
        if cmd == FlictSpec.CMDB_BEGIN_HEADER:
            if date == None:
                raise ValueError("Required property date not provided")
            if size == None:
                raise ValueError("Required property size not provided")
            if version == None:
                raise ValueError("Required property version not provided")
            elif not FlictSpec.isValidVersion(version):
                raise ValueError("Invalid value passed for property version.")
            byte_arr.append(
                FlictSpec.CMDB_BEGIN_HEADER |
                (version & FlictSpec.ATTR_HEADER_VERSION)
            )
            byte_arr.append(size & 0xFF)
            for n in reversed(range(8)):
                byte_arr.append((date >> (8 * n)) & 0xFF)
        elif cmd == FlictSpec.CMDB_BEGIN_PTREE_NODE:
            if order == None:
                raise ValueError("Required property order not provided")
            if size == None:
                raise ValueError("Required property size not provided")
            if type == None:
                raise ValueError("Required property type not provided")
            byte_arr.append(FlictSpec.CMDB_BEGIN_PTREE_NODE |
                ((order << 4) & FlictSpec.ATTR_PTREE_NODE_ORDER) |
                ((type << 2) & FlictSpec.ATTR_PTREE_NODE_TYPE) |
                (size & FlictSpec.ATTR_PTREE_NODE_SIZE)
            )
            if type >= 2:
                if freq == None:
                    raise ValueError("Required property freq not provided")
                byte_arr.append(freq & 0xFF)
        elif cmd == FlictSpec.CMDB_END:
            if end_count == None:
                raise ValueError("Required property end_count not provided")
            byte_arr.append(FlictSpec.CMDB_END | (end_count & FlictSpec.ATTR_END_COUNT))
        elif cmd == FlictSpec.CMDB_DEFINE_SHORTCUT:
            if size == None:
                raise ValueError("Required property size not provided")
            byte_arr.append(FlictSpec.CMDB_DEFINE_SHORTCUT | ((size >> 8) & 0x0F))
            byte_arr.append(size & 0xFF)
        else:
            raise ValueError("Invalid CMD provided!")

class Ngram:
    def __init__(self, tokens: List[str], freq: int, shortcut: Optional[str] = None,
                    shortcut_freq: Optional[int] = None):
        if len(tokens) == 0:
            raise ValueError("The token list must not be empty!")
        self.order = len(tokens)
        self.tokens = tokens
        self.freq = freq
        self.shortcut = shortcut

class FlictNode:
    def __init__(self, order: int, type: int, token: str, freq: Optional[int] = None):
        self.order: int = order
        self.type: int = type
        self.token: str = token
        self.freq: Optional[int] = None
        self.children: Dict[str, FlictNode] = {}

    def encode(self, byte_arr: bytearray):
        token_arr = bytearray(self.token, "utf-8")
        FlictSpec.writeCmd(byte_arr, FlictSpec.CMDB_BEGIN_PTREE_NODE,
            size=len(token_arr)-1, type=self.type, order=self.order-1, freq=self.freq)
        byte_arr.extend(token_arr)
        for child_node in self.children.values():
            child_node.encode(byte_arr)
        # if (byte_arr[-1] & FlictSpec.MASK_END) == FlictSpec.CMDB_END:
        #     last_end_count = (byte_arr[-1] & FlictSpec.ATTR_END_COUNT)
        #     if last_end_count < FlictSpec.ATTR_END_COUNT_MAX:
        #         del byte_arr[-1]
        #         end_count = last_end_count + 1
        #     else:
        #         end_count = 1
        # else:
        #     end_count = 1
        ## end_count always 1 on purpose because else there's a severe bug
        ## TODO: fix it
        FlictSpec.writeCmd(byte_arr, FlictSpec.CMDB_END, end_count=1)

class FlictRootNode(FlictNode):
    def __init__(self):
        self.header: Optional[str] = None
        self.order = 0
        self.type = -1
        self.token = ""
        self.freq = -1
        self.children = {}

    def encode(self, byte_arr: bytearray, version: int):
        if self.header == None:
            raise ValueError("Header must be specified!")
        header_arr = bytearray(self.header, "utf-8")
        FlictSpec.writeCmd(byte_arr, FlictSpec.CMDB_BEGIN_HEADER,
            version=version, size=len(header_arr), date=99)
        byte_arr.extend(header_arr)
        FlictSpec.writeCmd(byte_arr, FlictSpec.CMDB_END, end_count=1)
        for child_node in self.children.values():
            child_node.encode(byte_arr)

    # !! Currently only supports n-grams with order=1
    def insertNgram(self, ngram: Ngram):
        ptree_node = self
        ngram_pos = 0
        for token in ngram.tokens:
            pos = 0
            for c in token:
                if not c in ptree_node.children:
                    ptree_node.children[c] = FlictNode(ngram_pos + 1, FlictSpec.ATTR_PTREE_NODE_TYPE_CHAR, c)
                if pos + 1 >= len(token):
                    ptree_node.children[c].type = FlictSpec.ATTR_PTREE_NODE_TYPE_WORD
                    ptree_node.children[c].freq = ngram.freq
                ptree_node = ptree_node.children[c]
                pos += 1
            ngram_pos += 1


def clb_to_flict(src_path: str, dst_path: str):
    try:
        ptree = FlictRootNode()
        with io.open(src_path, "r", encoding="utf-8") as f_src:
            is_first = True
            for line in f_src.readlines():
                if is_first:
                    # Treat as header
                    ptree.header = line.rstrip()
                    is_first = False
                else:
                    line_list = line.rstrip()[6:].split(",f=")
                    word = unicodedata.normalize("NFC", line_list[0])
                    freq = int(line_list[1])
                    ptree.insertNgram(Ngram([word], freq))
        flict_bytes = bytearray()
        ptree.encode(flict_bytes, FlictSpec.VERSION_0)
        with io.open(dst_path, "wb") as f_dst:
            f_dst.write(flict_bytes)
        return True
    except ValueError as e:
        print(e)
        return False

if __name__ == "__main__":
    clb_to_flict("./.dicttool/combined-list-en.txt", "./.dicttool/en.flict")
