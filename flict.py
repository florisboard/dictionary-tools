import json
import io
import unicodedata

__FLICT_CMD_BEGIN_HEADER =      0x1
__FLICT_CMD_BEGIN_SECTION =     0x2
__FLICT_CMD_END =               0x3

__FLICT_BEGIN_SECTION_128 =     0x00
__FLICT_BEGIN_SECTION_16384 =   0x80
__FLICT_BEGIN_HEADER =          0xC0
__FLICT_END =                   0xF0

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

def __encode_inner(byte_arr: bytearray, word: str, section: dict):
    word_bytes = bytearray(word, "utf-8")
    __encode_cmd_block(byte_arr, __FLICT_CMD_BEGIN_SECTION, len(word_bytes))
    if "$f" in section:
        byte_arr.append(int(section["$f"]) & 0xFF)
    else:
        byte_arr.append(0x00)
    byte_arr.extend(word_bytes)
    for key in section:
        if key == "$f":
            pass
        else:
            __encode_inner(byte_arr, key, section[key])
    last_byte = byte_arr[-1]
    if last_byte & 0xF0 == 0xF0:
        del byte_arr[-1]
        __encode_cmd_block(byte_arr, __FLICT_CMD_END, (last_byte & 0x0F) + 1)
    else:
        __encode_cmd_block(byte_arr, __FLICT_CMD_END, 1)

def __encode(obj: dict):
    byte_arr = bytearray()
    for key in obj:
        if key == "$h":
            header_str = bytearray(obj[key], "utf-8")
            __encode_cmd_block(byte_arr, __FLICT_CMD_BEGIN_HEADER, len(header_str))
            byte_arr.extend(header_str)
            __encode_cmd_block(byte_arr, __FLICT_CMD_END, 1)
        else:
            __encode_inner(byte_arr, key, obj[key])
    return byte_arr

def clb_to_flict(src_path: str, dst_path: str):
    try:
        flict_prep_obj = {}
        worddict = {}
        with io.open(src_path, "r", encoding="utf-8") as f_src:
            is_first = True
            for line in f_src.readlines():
                if is_first:
                    # Treat as header
                    flict_prep_obj.update({"$h": line.rstrip()})
                    is_first = False
                else:
                    line_list = line.rstrip()[6:].split(",f=")
                    word = unicodedata.normalize("NFC", line_list[0])
                    freq = int(line_list[1])
                    worddict.update({word:freq})
        wordlist = sorted(worddict)
        wordlist_index = 0
        for word in wordlist:
            freq = worddict[word]
            prep_obj = flict_prep_obj
            pos = 0
            for c in word:
                if pos + 1 >= len(word):
                    if c not in prep_obj:
                        prep_obj.update({c:{}})
                    prep_obj[c].update({"$f": freq})
                else:
                    if c in prep_obj:
                        pass
                    else:
                        if wordlist_index + 1 >= len(wordlist):
                            if c not in prep_obj:
                                prep_obj.update({c:{}})
                        elif wordlist[wordlist_index + 1].startswith(word[0:pos + 1]):
                            if c not in prep_obj:
                                prep_obj.update({c:{}})
                        else:
                            wr = word[pos:]
                            if wr not in prep_obj:
                                prep_obj.update({wr:{}})
                            prep_obj[wr].update({"$f": freq})
                            break
                    prep_obj = prep_obj[c]
                    pos += 1
            wordlist_index += 1
        # with io.open("test.flict.json", "w") as f:
        #     f.write(json.dumps(flict_prep_obj, separators=(',', ':')))
        with io.open(dst_path, "wb") as f_dst:
            f_dst.write(__encode(flict_prep_obj))
        return True
    except ValueError as e:
        print(e)
        return False

#clb_to_flict("./.dicttool/combined-list-en.txt", "./.dicttool/en.flict")
