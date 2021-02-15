# Flictionary: A binary dictionary file format
Flictionary is a binary dictionary file format primarily developed for use in
the FlorisBoard project, hence the name "Floris + Dictionary" -> "Flictionary".
To distinguish it from other binary dictionary files, the convention is to
give a Flictionary file the extension ".flict".

The Flictionary format is focused on minimizing the size of the file without
any data loss. It is partly achieved by trying to minimze command bytes and to
minimize repetion in the data bytes by using a property tree and addresses for
re-occuring words.

Each Flictionary file is required to have exactly one header at the beginning
of the file. If a Flictionary file does not start with the "begin-header"
command byte, it must immediately be discarded and invalidated.

The encoding of all characters included in the data scopes are strictly
restricted to UTF-8.

NOTE: The current version of this spec is v0. While in v0, the spec my change
at any given time and may break things. When this spec file releases in v1,
the spec of the Flictionary file format is stable and changes may only be done
in sub-sequent versions (v2, v3, ...).

## General Structure
Flictionaries allow for housing a unigram wordlist with frequencies, as well as
storing n-gram models for next-word predictions. The file format does not limit
the size of the n-grams, so you can efficiently store bigrams, trigrams, 4-grams
and so on. The limit theretically is only the file size.

In general, the basic skeleton structure behind each Flictionary is as follows:

```
{header}
{ptree (unigram wordlist)}
{n-gram tree}
```

### Header
The header contains viable metadata about the version of this file, the creation
date and the description. Without a present header, a Flictionary file is
incomplete and cannot be parsed.

### Ptree (Unigram wordlist)
This property tree represents a unigram list, where each word has a frequency
attached to it, alongside a unique 24-bit address which is used in the n-gram
tree below. It is the responibility of the encoder to ensure that the addresses
are unique between them. The address field can be omitted if the Z-flag in the
header is set to False.

### N-gram tree
This tree is also a form o property tree, which allows to store any count of
n-grams. This tree is only included if the Z-flag in the header is set to True.
N-grams can only contain words if the word also exists in the unigram wordlist.
In the last node of each n-gram, the frequency of the n-gram is defined.

## Scopes

### Command Scope
In this scope, every byte read has to be checked against the set of command
bytes. Based on the most-significant bits, it is easly to detect which
command will follow. If no other bytes have been read, this scope is
automatically the active one.

Table of valid command bytes:

```
    0ttsssss [ffffffff] [aaaaaaaa]    begin-ptree-node
        This command marks the beginning to a new property tree node and must
        only be used when in the root level of the file or as a child of a
        parent ptree-node.
        t ... The type of this node. A zero value indicates that this node does
              not mark the end of a word. A value in the range of [1;3] marks
              this word as a valid end point and sets the length of the address
              field to t in bytes. If the Z-flag in the header is set to False,
              any value within [1;3] may be used to mark this as a valid word.
        f ... The frequency of the word this end node represents. A zero value
              indicates that this word is potentionally offensive or crude, but
              may be used for spellchecking purposes only. A value in the range
              [1;255] marks this word as suitable for spellchecking and
              suggestions. This field must only be provided if t >= 0x1.
        a ... The address of this word, either of length 1, 2 or 3 bytes,
              depending on t. This field must only be provided if t >= 0x1 and
              if the Z-flag in the header is set to True.

    10nnnnnn                          end
        This command marks the end to a previously opened header, ptree node or
        n-gram node.
        n ... A 6-bit value indicating the count of end sequences this byte
              represents. Valid value range is [1;63].

    110zvvvv  ssssssss  dddddddd      begin-header
        This command byte indicates the beginning of a header and must be the
        first byte in the binary file to appear, else the file cannot be inter-
        preted corrently. Exactly s bytes after this command byte set have to
        be interpreted in Data Scope.
        z ... The Z-flag indicates if this Flictionary houses n-grams or not.
              If False, all address fields in this file must be omitted and the
              begin-n-gram-node command byte must not be used.
        v ... A 4-bit value defining the version of Flictionary spec this file
              follows. Valid values are all released fiel spec versions.
        s ... A 8-bit value indicating the length of the header that follows
              (raw description etc.). Valid value range: [1;255].
        d ... A 64-bit value defining the date of creation of this file as a
              UNIX timestamp.

    111110tt [ffffffff] [aaaaaaaa]    begin-n-gram-node
        This command byte indicates the beginning of a n-gram node. Must only
        be used if the Z-flag in the header is set to True.
        t ... A 2-bit value defining the type of the address. A zero-value
              indicates that this n-gram node does not mark the end of a n-gram.
              A value in the range [1;3] indicates the length of the address a
              which will follow in bytes.
        f ... A 8-bit value defining the frequency of this n-gram. This value
              must only be provided if t >= 0x1. Valid value range is [0;255].
        a ... The address of the word in the unigram wordlist if b >= 0x1.
              The lengtn of the address is either 1, 2 or 3 bytes, depending on
              the value of t. Tis referencing is done to save space, no data
              related to this word is inherited, except the exact byte sequence
              encoded as UTF-8.
```

### Data Scope
In this scope, every byte that is read has to be interpreted as the data.
The encoding of the data is UTF-8 only. The length of the data is determined
by the previous section's size value.
