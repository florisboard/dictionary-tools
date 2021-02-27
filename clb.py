#!/usr/bin/env python3
# encoding: utf-8

import gzip
import msgpack
import io
import regex
import time

STR_VALIDATE_REGEX = r"^((\p{L}\p{M}*)|\'|\-)+$"

def __validate_str(str):
    return regex.search(STR_VALIDATE_REGEX, str) != None and len(str) != 0

def __freq_for_index(index, len_list):
    """
    Calculates the frequency for a given index based on the list length.
    The base is f(x) = -(x^2) + 1
    The result, which is always between 0.0 and 1.0, is then adjusted to be
    in the interval [15;255]. This value can then be used in the combined list.
    """
    x = index / len_list
    return int(240 * (-(x**2) + 1) + 15)

def __header(lang_code):
    return "dictionary=main:{lang_code},locale={lang_code},description=Auto-generated dictionary for {lang_code},date={date},version=1\n" \
            .format(lang_code=lang_code,date=int(time.time()*1000))

def cBpack(lang_code, src_path, swear_path, dst_path):
    """
    Works with a cBpack source and builds a combined list.
    Explaination of cBpack: https://github.com/LuminosoInsight/wordfreq/blob/7a742499a42a6539be772ab26b6460d7e160ae04/wordfreq/__init__.py#L37-L76
    Frequency calculation adjusted to work with 15..255 format
    """
    with gzip.open(src_path, "rb") as f_src:
        data_raw = msgpack.load(f_src, raw=False)
    header = data_raw[0]
    if (
        not isinstance(header, dict) or header.get("format") != "cB"
        or header.get("version") != 1
    ):
        raise ValueError("Unexpected header: {}".format(header))
    data = data_raw[1:]
    data_sanitized = []
    for innerlist in data:
        sanitized_list = []
        for word in innerlist:
            word_sanitized = word.strip()
            if (__validate_str(word_sanitized)):
                sanitized_list.append(word_sanitized)
        if len(sanitized_list) > 0:
            data_sanitized.append(sanitized_list)
    swear_words = []
    with io.open(swear_path, encoding="utf-8") as f_swear:
        for swear_word in f_swear.readlines():
            swear_word = swear_word.strip()
            if len(swear_word) > 0:
                if swear_word[0] != "#":
                    swear_words.append(swear_word)
    index = 0
    with io.open(dst_path, "w", encoding="utf-8") as f_dst:
        # Write header of combined list first
        f_dst.write(__header(lang_code))
        len_list = len(data_sanitized)
        for innerlist in data_sanitized:
            freq = __freq_for_index(index, len_list)
            for word in innerlist:
                if word in swear_words:
                    adjusted_freq = 0
                else:
                    adjusted_freq = freq
                f_dst.write(" word={},f={}\n".format(word, adjusted_freq))
            index += 1
