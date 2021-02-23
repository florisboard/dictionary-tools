# Flictionary: A binary dictionary file format
Flictionary is a binary dictionary file format primarily developed for use in
the FlorisBoard project, hence the name "Floris + Dictionary" -> "Flictionary".
To distinguish it from other binary dictionary files, the convention is to
give a Flictionary file the extension ".flict".

The Flictionary format is focused on minimizing the size of the file without
any data loss. It is partly achieved by trying to minimze command bytes and to
minimize repetion in the data bytes by using a property tree to store the words.

Each Flictionary file is required to have exactly one header at the beginning
of the file. If a Flictionary file does not start with the "begin-header"
command byte, it must immediately be discarded and invalidated.

The encoding of all characters included in the data scopes are strictly
restricted to UTF-8, other encodings are not supported.

NOTE: The current version of this spec is v0. While in v0, the spec may change
at any given time and may break things. When this spec file releases in v1,
the spec of the Flictionary file format is stable and changes may only be done
in sub-sequent versions (v2, v3, ...).

## General Structure
Flictionaries allow for housing a unigram wordlist with frequencies, as well as
storing n-gram models for next-word predictions. The file format does limit the
size of the n-grams to the range unigram..8-gram (both inclusive), which should
be more than sufficient to house a language model.

In general, the basic skeleton structure behind each Flictionary is as follows:

```
{header}
{n-gram tree}
```

### Header
The header contains viable metadata about the version of this file, the creation
date and the description. Without a present header, a Flictionary file is
incomplete and cannot be parsed.

### N-gram tree
The n-gram tree is a propery tree at its core and stores all words as well as
n-grams space efficiently in one tree. The maximum order of n-grams is 8.

## Scopes

### Command Scope
In this scope, every byte read has to be checked against the set of command
bytes. Based on the most-significant bits, it is easy to detect which
command will follow. If no other bytes have been read, this scope is
automatically the active one.

Table of valid command bytes:

```
    0nnnttss [ffffffff] <letter>                begin-ptree-node
        This command marks the beginning to a new property tree node and must
        only be used when in the root level of the file or as a child of a
        parent ptree-node.
        n ... A 3-bit value indicating the order of the current n-gram. Note
              that this value is zero-aligned, so n=0 means 1 which corresponds
              to an unigram. This representation allows up to an 8-gram.
        t ... The type of this node. Valid values:
               0: a character of a word not marking the end of a word.
               1: a valid end point of a word, which does not have a freqency
                  attached (used as a filler for a higher-order n-gram).
               2: a valid end point of a word.
               3: a valid end point of a shortcut, meaning it must not be used
                  by spellchecking but can be used by the suggestion algorithm
                  to suggest another word, based on the define-shortcut commands
                  inside this node.
        s ... A 2-bit value indicating the size of the following Unicode letter
              in bytes, excluding the freq field. Note that the value is zero
              aligned, meaning that a value of s=1 means 2 bytes, etc.
        f ... The frequency of the word this end node represents. A zero value
              indicates that this word is potentionally offensive or crude, but
              may be used for spellchecking purposes only. A value in the range
              [1;255] marks this word as suitable for spellchecking and
              suggestions. This field must only be provided if t >= 2.

    10nnnnnn                                    end
        This command marks the end to a previously opened header or ptree node.
        n ... A 6-bit value indicating the count of end sequences this byte
              represents. Valid value range is [1;63].

    110vvvvv  ssssssss  dddddddd                begin-header
        This command byte indicates the beginning of a header and must be the
        first byte in the binary file to appear, else the file cannot be inter-
        preted corrently. Exactly s bytes after this command byte set have to
        be interpreted in Data Scope.
        v ... A 5-bit value defining the version of Flictionary spec this file
              follows. Valid values are all released file spec versions.
        s ... A 8-bit value indicating the length of the header that follows
              (raw description etc.). Valid value range: [1;255].
        d ... A 64-bit value defining the date of creation of this file as a
              UNIX timestamp.

    1110ssss  ssssssss  ffffffff  <word>        define-shortcut
        This command byte defines a shortcut for a word. Must only be used when
        the parent node's type is 3.
        s ... A 12-bit value defining the utf-8 encoded word in bytes.
        f ... The frequency of the word this shortcut represents. A zero value
              indicates that this word is potentionally offensive or crude, but
              may be used for spellchecking purposes only. A value in the range
              [1;255] marks this shortcut as suitable for spellchecking and
              suggestions.
```

### Data Scope
In this scope every byte that is read has to be interpreted as the data.
The encoding of the data is UTF-8 only. The length of the data is determined
by the previous section's size value.
