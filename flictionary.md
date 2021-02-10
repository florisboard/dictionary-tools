# Flictionary: A binary dictionary file format

Flictionary is a binary dictionary file format primarily developed for use in
the FlorisBoard project, hence the name "Floris + Dictionary" -> "Flictionary".
To distinguish it from other binary dictionary files, the convention is to
give a Flictionary file the extension ".flict".

The Flictionary format is focused on minimizing the size of the file without
any data loss. It is partly achieved by trying to minimze command bytes and to
minimize repetion in the data bytes by using a sub-grouping concept.

Each Flictionary file is required to have exactly one header at the beginning
of the file. If a Flictionary file does not start with the "begin-header"
command byte, it must immediately be discarded and invalidated.

## General Structure

In general, this is the structure behind each Flictionary, visualized as plain
text. A "{" indicates a begin-section byte, a "}" indicates an end byte with n
count. Spaces, new-lines and indentation are only for visualization.

```
{h "Dictionary-header, no formatting rules" }1
{ 245 a
    { 246 n
        { 234 d }1
        { 0 n
            { 24 o }2
        { 233 t
            { 23 i
                { 0 q
                    { 0 u
                        { 11 e }7
{ 0 b
    ...
}1
```

The above structure contains the following words + frequencies:
- a 245
- an 246
- and 234
- anno 24
- ant 233
- anti 23
- antique 11

## Scopes

### Command Scope

In this scope, every byte read has to be checked against the set of command
bytes. Based on the most-significant bits, it is easly to detect which
command will follow. If no other bytes have been read, this scope is auto-
matically the active one.

Table of valid command bytes:

```
    0sssssss ffffffff               begin-section   [2-byte command]
        This command byte indicates the beginning of a section. Exactly s bytes
        after this command byte set have to be interpreted in Data Scope.
        s ... A 7-bit value indicating the length of the character or word of
              this section ["data"] in bytes, excluding the frequency byte.
              Valid value range: [1;127].
        f ... A 8-bit value defining the frequency of this section. A 0-value
              indicates that this group does not mark the end of an word and
              only serves as a filler-section. A value in [1;255] marks this
              section as a valid end point of a word with the frequency f.

    10ssssss ssssssss ffffffff      begin-section   [3-byte command]
        This command byte also indicates the beginning of a section, but allows
        for a bigger data size block to be defined. Exactly s bytes after this
        command byte set have to be interpreted in Data Scope.
        s ... A 14-bit value indicating the length of the character or word of
              this section ["data"] in bytes, excluding the frequency byte.
              Valid value range: [1;16383].
        f ... A 8-bit value defining the frequency of this section. A 0-value
              indicates that this group does not mark the end of an word and
              only serves as a filler-section. A value in [1;255] marks this
              section as a valid end point of a word with the frequency f.

    110sssss ssssssss               begin-header    [2-byte command]
        This command byte indicates the beginning of a header. Exactly s bytes
        after this command byte set have to be interpreted in Data Scope.
        s ... A 13-bit value indicating the length of the header that follows
              ["data"]. Valid value range: [1;8191].

    1111nnnn                        end             [1-byte command]
        This command byte indicates the end for exactly n sections. The
        following byte has to be interpreted in the Command Scope.
        n ... A 4-bit value indicating the count of sections to close. Valid
              value range: [1;15].
```

### Data Scope
In this scope, every byte that is read has to be interpreted as the data.
The encoding of the data is UTF-8 only. The length of the data is determined
by the previous section's size value.
